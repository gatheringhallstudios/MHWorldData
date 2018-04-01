import sqlalchemy.orm
import src.db as db

from src.util import ensure, ensure_warn, get_duplicates

from src.data import (
    set_languages, load_base_map, 
    load_data_map, load_split_data_map
)

output_filename = 'mhw.db'
supported_languages = ['en']
supported_ranks = ['lr', 'hr']
set_languages(supported_languages)

monster_map = load_base_map("monsters/monster_base.json")
skill_map = load_base_map("skills/skill_base.json")
item_map = load_base_map("items/item_base.json")
armor_map = load_base_map("armors/armor_base.json")
armorset_map = load_base_map("armors/armorset_base.json")
weapon_map = load_base_map("weapons/weapon_base.json")
decoration_map = load_base_map("decorations/decoration_base.json")

def build_monsters(session : sqlalchemy.orm.Session):
    # Load additional files
    monster_data = load_data_map(monster_map, "monsters/monster_data.json")

    for entry in monster_data.values():
        monster_name = entry.name('en')

        monster = db.Monster(id=entry.id)
        monster.size = entry['size']

        # todo: allow looping over language map entries for a row
        for language in supported_languages:
            monster.translations.append(db.MonsterText(
                lang_id=language,
                name=entry.name(language),
                description=entry['description'][language]
            ))

        for body_part, values in entry['hitzones'].items():
            monster.hitzones.append(db.MonsterHitzone(
                body_part = body_part,
                **values
            ))

        session.add(monster)
            
    print("Built Monsters")

def build_skills(session : sqlalchemy.orm.Session):
    for id, entry in skill_map.items():
        skilltree = db.SkillTree(id=id)

        for language in supported_languages:
            skilltree.translations.append(db.SkillTreeText(
                lang_id=language,
                name=entry.name(language),
                description=entry['description'][language]
            ))

            for effect in entry['effects']:
                session.add(db.Skill(
                    skilltree_id=id,
                    lang_id=language,
                    level=effect['level'],
                    description=effect['description'][language]
                ))

        session.add(skilltree)
    
    print("Built Skills")

def build_items(session : sqlalchemy.orm.Session):
    # Only item names exist now...so this is simple
    for id, entry in item_map.items():
        item = db.Item(id=id)

        for language in supported_languages:
            item.translations.append(db.ItemText(
                lang_id=language,
                name=entry.name(language)
            ))

        session.add(item)
    
    print("Built Items")

def build_armor(session : sqlalchemy.orm.Session):
    # Write entries for all armor set names first
    for id, entry in armorset_map.items():
        for language in supported_languages:
            session.add(db.ArmorSet(
                id=id,
                lang_id=language,
                name=entry.name(language)
            ))

    data_map = load_data_map(armor_map, 'armors/armor_data.json')
    for armor_id, entry in data_map.items():
        armor_name_en = entry.name('en')

        armor = db.Armor(id = armor_id)
        armor.rarity = entry['rarity']
        armor.armor_type = entry['armor_type']
        armor.male = entry['male']
        armor.female = entry['female']
        armor.slot_1 = entry['slots'][0]
        armor.slot_2 = entry['slots'][1]
        armor.slot_3 = entry['slots'][2]
        armor.defense_base = entry['defense_base']
        armor.defense_max = entry['defense_max']
        armor.defense_augment_max = entry['defense_augment_max']
        armor.fire = entry['fire']
        armor.water = entry['water']
        armor.thunder = entry['thunder']
        armor.ice = entry['ice']
        armor.dragon = entry['dragon']

        armorset_id = armorset_map.id_of("en", entry['set'])
        ensure(armorset_id, f"Armorset {entry['set']} in Armor {armor_name_en} does not exist")
        armor.armorset_id = armorset_id

        for language in supported_languages:
            armor.translations.append(db.ArmorText(
                lang_id=language, 
                name=entry.name(language)
            ))

        # Armor Skills
        for skill, level in entry['skills'].items():
            skill_id = skill_map.id_of('en', skill)
            ensure(skill_id, f"Skill {skill} in Armor {armor_name_en} does not exist")
            
            armor.skills.append(db.ArmorSkill(
                skill_id = skill_id,
                level = level
            ))
        
        # Armor Crafting
        for item, quantity in entry['craft'].items():
            item_id = item_map.id_of('en', item)
            ensure(item_id, f"Item {item} in Armor {armor_name_en} does not exist")
            
            armor.craft_items.append(db.ArmorRecipe(
                item_id = item_id,
                quantity = quantity
            ))

        session.add(armor)

    print("Built Armor")

def build_weapons(session : sqlalchemy.orm.Session):
    weapon_data = load_split_data_map(weapon_map, "weapons/weapon_data")

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

        # todo: sharpness, coatings, ammo

        # Note: High probably the way this is stored in data will be refactored
        # Possibilities are either split weapon_data files, or separated sub-data files
        weapon.glaive_boost_type = entry.get('glaive_boost_type', None)
        weapon.deviation = entry.get('deviation', None)
        weapon.special_ammo = entry.get('special_ammo', None)
        
        weapon.craftable = bool(entry.get('craft', False))
        weapon.final = weapon_id in all_final

        if entry.get('previous', None):
            previous_weapon_id = weapon_map.id_of("en", entry['previous'])
            ensure(previous_weapon_id, f"Weapon {entry['previous']} does not exist")
            weapon.previous_weapon_id = previous_weapon_id

        # Add language translations
        for language in supported_languages:
            weapon.translations.append(db.WeaponText(
                lang_id = language,
                name = entry.name(language)
            ))

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
        
        session.add(weapon)

    print("Built Weapons")

def build_decorations(session : sqlalchemy.orm.Session):
    "Performs the build process for decorations. Must be done after skills"

    decoration_chances = load_data_map(decoration_map, "decorations/decoration_chances.json")

    for decoration_id, entry in decoration_map.items():
        skill_id = skill_map.id_of('en', entry['skill_en'])
        ensure(skill_id, f"Decoration {entry.name('en')} refers to " +
            f"skill {entry['skill_en']}, which doesn't exist.")

        chance_data = decoration_chances.get(decoration_id, None)
        ensure(chance_data, "Missing chance data for " + entry.name('en'))
        
        decoration = db.Decoration(
            id=decoration_id,
            rarity=entry['rarity'],
            slot=entry['slot'],
            skill_id=skill_id,
            mysterious_feystone_chance=chance_data['mysterious_feystone_chance'],
            glowing_feystone_chance=chance_data['glowing_feystone_chance'],
            worn_feystone_chance=chance_data['worn_feystone_chance'],
            warped_feystone_chance=chance_data['warped_feystone_chance']
        )

        for language in supported_languages:
            decoration.translations.append(db.DecorationText(
                lang_id=language,
                name=entry.name('en')
            ))

        session.add(decoration)

    print("Built Decorations")

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
    build_decorations(session)
    build_monster_rewards(session)
    print("Finished build")
