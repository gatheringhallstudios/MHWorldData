import sqlalchemy.orm
import src.db as db

from src.util import ensure, ensure_warn, get_duplicates

from src.data import (
    set_languages, load_data_map, load_translate_map, load_language_data_dir
)

output_filename = 'mhw.db'
supported_languages = ['en']
supported_ranks = ['lr', 'hr']
set_languages(supported_languages)

monster_map = load_translate_map("monsters/monster_names.json")
skill_map = load_translate_map("skills/skill_names.json")
item_map = load_translate_map("items/item_names.json")
armor_map = load_translate_map("armors/armor_names.json")
armorset_map = load_translate_map("armors/armor_set_names.json")
weapon_map = load_translate_map("weapons/weapon_names.json")

def build_monsters(session : sqlalchemy.orm.Session):
    # Load additional files
    monster_data = load_data_map(monster_map, "monsters/monster_data.json")
    description = load_language_data_dir(monster_map, 'monsters/monster_descriptions')

    for entry in monster_data.values():
        monster_name = entry.name('en')

        monster = db.Monster(id=entry.id)
        monster.size = entry['size']
        session.add(monster)

        # todo: allow looping over language map entries for a row
        for language in supported_languages:
            monster_text = db.MonsterText(id=entry.id, lang_id=language)
            monster_text.name = monster_map[entry.id][language]
            monster_text.description = description[entry.id][language][f'description_{language}']
            session.add(monster_text)

        for body_part, values in entry['hitzones'].items():
            session.add(db.MonsterHitzone(
                monster_id = entry.id,
                body_part = body_part,
                **values
            ))
            
    print("Built Monsters")


def build_skills(session : sqlalchemy.orm.Session):
    skill_descriptions = load_language_data_dir(skill_map, 'skills/skills')
    for row in skill_map:
        skilltree = db.SkillTree(id=row.id)
        session.add(skilltree)

        for language in supported_languages:
            skilldata_row = skill_descriptions[row.id][language] 

            name = row[language]
            description = skilldata_row[f'description_{language}']

            session.add(db.SkillTreeText(
                id=row.id, lang_id=language, name=name, description=description))

            for effect in skilldata_row['effects']:
                level = effect['level']
                effect_description = effect[f'description_{language}']
                session.add(db.Skill(
                    skilltree_id=row.id,
                    lang_id=language,
                    level = level,
                    description=effect_description
                ))
    
    print("Built Skills")

def build_items(session : sqlalchemy.orm.Session):
    # Only item names exist now...so this is simple
    for row in item_map:
        item = db.Item(id=row.id)
        session.add(item)

        for language in supported_languages:
            item_text = db.ItemText(id=row.id, lang_id=language)
            item_text.name = row[language]
            session.add(item_text)
    
    print("Built Items")

def build_armor(session : sqlalchemy.orm.Session):
    # Write entries for all armor set names first
    for (id, language, name) in armorset_map.all_items():
        armorset = db.ArmorSet(id=id, lang_id=language, name=name)
        session.add(armorset)

    data_map = load_data_map(armor_map, 'armors/armor_data.json')
    for entry in data_map.values():
        armor_name_en = entry.name('en')

        armor = db.Armor(id = entry.id)
        armor.rarity = entry['rarity']
        armor.armor_type = entry['armor_type']
        armor.male = entry['male']
        armor.female = entry['female']
        armor.slot_1 = entry['slots'][0]
        armor.slot_2 = entry['slots'][1]
        armor.slot_3 = entry['slots'][2]
        armor.defense = entry['defense']
        armor.fire = entry['fire']
        armor.water = entry['water']
        armor.thunder = entry['thunder']
        armor.ice = entry['ice']
        armor.dragon = entry['dragon']

        armorset_id = armorset_map.id_of("en", entry['set'])
        if not armorset_id:
            raise Exception(f"ERROR: Armorset {data['set']} in Armor {armor_name_en} does not exist")
        armor.armorset_id = armorset_id

        session.add(armor)

        for language in supported_languages:
            armor_name = entry.name(language)
            armor_text = db.ArmorText(id=entry.id, lang_id=language, name=armor_name)
            session.add(armor_text)

        # Armor Skills
        for skill, level in entry['skills'].items():
            skill_id = skill_map.id_of('en', skill)
            ensure(skill_id, f"Skill {skill} in Armor {armor_name_en} does not exist")
            
            session.add(db.ArmorSkill(
                armor_id = entry.id,
                skill_id = skill_id,
                level = level
            ))
        
        # Armor Crafting
        for item, quantity in entry['craft'].items():
            item_id = item_map.id_of('en', item)
            ensure(item_id, f"Item {item} in Armor {armor_name_en} does not exist")
            
            session.add(db.ArmorRecipe(
                armor_id = entry.id,
                item_id = item_id,
                quantity = quantity
            ))

    print("Built Armor")

def build_weapons(session : sqlalchemy.orm.Session):
    weapon_data = load_data_map(weapon_map, "weapons/weapon_data.json")

    # Prepass to determine which weapons are "final"
    # All items that are a previous to another are "not final"
    all_final = set(weapon_data.keys())
    for entry in weapon_data.values():
        if not entry.get('previous', None):
            continue
        try:
            prev_id = weapon_map.id_of('en', entry['previous'])
            all_final.remove(prev_id)
        except KeyError:
            pass

    for weapon_id, entry in weapon_data.items():
        weapon = db.Weapon(id = weapon_id)
        weapon.weapon_type = entry['weapon_type']
        weapon.rarity = entry['rarity']
        weapon.attack = entry['attack']
        weapon.slot_1 = entry['slots'][0]
        weapon.slot_2 = entry['slots'][1]
        weapon.slot_3 = entry['slots'][2]

        weapon.element_type = entry['element_type']
        weapon.element_damage = entry['element_damage']
        weapon.element_hidden = entry['element_hidden']

        # todo: sharpness, coatings, ammo, deviation, special ammo
        
        weapon.craftable = bool(entry.get('craft', False))
        weapon.final = weapon_id in all_final

        if entry.get('previous', None):
            previous_weapon_id = weapon_map.id_of("en", entry['previous'])
            ensure(previous_weapon_id, f"Weapon {entry['previous']} does not exist")
            weapon.previous_weapon = previous_weapon_id

        session.add(weapon)

        # Add language translations
        for language in supported_languages:
            weapon_name = entry.name(language)
            session.add(db.WeaponText(id=weapon_id, lang_id=language, name=weapon_name))

        # Add crafting/upgrade recipes
        for recipe_type in ('craft', 'upgrade'):
            recipe = entry.get(recipe_type, {}) or {}
            for item, quantity in recipe.items():
                item_id = item_map.id_of("en", item)
                ensure(item_id, f"Item {item_id} in weapon {entry.name('en')} does not exist")
                session.add(db.WeaponRecipe(
                    weapon_id = weapon_id,
                    item_id = item_id,
                    quantity = quantity,
                    recipe_type = recipe_type
                ))

    print("Built Weapons")

def build_monster_rewards(session : sqlalchemy.orm.Session):
    "Performs the build process for monster rewards. Must be done AFTER monsters and items"
    
    monster_reward_data = load_data_map(monster_map, "monsters/monster_rewards.json")
    
    # These are validated for 100% drop rate EXACT.
    # Everything else is checked for "at least" 100%
    single_drop_conditions = ("Body Carve", "Tail Carve", "Shiny Drop", "Capture")

    for entry in monster_reward_data.values():
        monster_id = entry.id
        monster_name = entry.name('en')

        for condition, sub_condition in entry.get('rewards', {}).items():
            for rank, rewards in sub_condition.items():
                # Ensure correct rank
                ensure(rank in supported_ranks, f"Unsupported rank {rank} in {monster_name} rewards")

                # Ensure percentage is correct (at or greater than 100)
                percentage_sum = sum((r['percentage'] for r in rewards), 0)
                error_start = f"Rewards %'s for monster {monster_name} (rank {rank} condition {condition})"
                if condition in single_drop_conditions:
                    ensure_warn(percentage_sum == 100, f"{error_start} does not sum to 100")
                else:
                    ensure_warn(percentage_sum >= 100, f"{error_start} does not sum to at least 100")

                # check for duplicates (if the condition is relevant)
                if condition in single_drop_conditions:
                    duplicates = get_duplicates((r['item_en'] for r in rewards))
                    ensure_warn(not duplicates, f"Monster {monster_name} contains " +
                        f"duplicate rewards {','.join(duplicates)} in rank {rank} " +
                        f"for condition {condition}")

                for reward in rewards:
                    item_name = reward['item_en']
                    item_id = item_map.id_of('en', item_name)
                    ensure(item_id, f"ERROR: item reward {item_name} in monster {monster_name} does not exist")

                    session.add(db.MonsterReward(
                        monster_id = monster_id,
                        condition = condition,
                        rank = rank,
                        item_id = item_id,
                        stack_size = reward['stack'],
                        percentage = reward['percentage']
                    ))

    print("Built Monster Rewards")


sessionbuilder = db.recreate_database(output_filename)

with db.session_scope(sessionbuilder) as session:
    build_monsters(session)
    build_skills(session)
    build_items(session)
    build_armor(session)
    build_weapons(session)
    build_monster_rewards(session)
    print("Finished build")
