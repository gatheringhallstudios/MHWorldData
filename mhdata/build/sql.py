import sqlalchemy.orm
import mhdata.sql as db

from mhdata.io import DataMap
from mhdata.util import ensure, ensure_warn, get_duplicates

import mhdata.load.cfg as cfg

supported_languages = cfg.supported_languages
all_languages = cfg.all_languages
incomplete_languages = cfg.incomplete_languages

from .objectindex import ObjectIndex

def build_sql_database(output_filename, mhdata):
    "Builds a SQLite database and outputs to output_filename"
    sessionbuilder = db.recreate_database(output_filename)

    with db.session_scope(sessionbuilder) as session:
        # Add languages before starting the build
        for language in supported_languages:
            session.add(db.Language(
                id=language,
                name=all_languages[language],
                is_complete=(language not in incomplete_languages)
            ))

        # Build the individual components
        # These functions are defined lower down in the file
        build_items(session, mhdata)
        build_locations(session, mhdata)
        build_monsters(session, mhdata)
        build_skills(session, mhdata)
        build_armor(session, mhdata)
        build_weapons(session, mhdata)
        build_decorations(session, mhdata)
        build_charms(session, mhdata)
        
    print("Finished build")


def build_items(session : sqlalchemy.orm.Session, mhdata):
    for id, entry in mhdata.item_map.items():
        item = db.Item(id=id)
        item.category = entry['category']
        item.rarity = entry['rarity'] or 0
        item.buy_price = entry['buy_price'] or 0
        item.sell_price = entry['sell_price'] or 0
        item.carry_limit = entry['carry_limit'] or 0

        for language in supported_languages:
            item.translations.append(db.ItemText(
                lang_id=language,
                name=entry.name(language),
                description=entry['description'].get(language, None)
            ))

        session.add(item)
    
    print("Built Items")

def build_locations(session : sqlalchemy.orm.Session, mhdata):
    for location_id, entry in mhdata.location_map.items():
        location_name = entry['name']['en']

        for language in supported_languages:
            session.add(db.Location(
                id=location_id,
                lang_id=language,
                name=entry.name(language)
            ))

        for item_entry in entry['items']:
            item_lang = item_entry['item_lang']
            item_name = item_entry['item']
            item_id = mhdata.item_map.id_of(item_lang, item_name)
            ensure(item_id, f"item {item_name} in monster {location_name} does not exist")

            session.add(db.LocationItem(
                location_id=location_id,
                rank=item_entry['rank'],
                item_id=item_id,
                stack=item_entry['stack'],
                percentage=item_entry['percentage'],
            ))
            
    print("Built locations")

def build_monsters(session : sqlalchemy.orm.Session, mhdata):
    item_map = mhdata.item_map
    location_map = mhdata.location_map
    monster_map = mhdata.monster_map
    monster_reward_conditions_map = mhdata.monster_reward_conditions_map

    # Save conditions first
    for condition_id, entry in monster_reward_conditions_map.items():
        for language in supported_languages:
            session.add(db.MonsterRewardConditionText(
                id=condition_id,
                lang_id=language,
                name=entry.name(language)
            ))

    # Save monsters
    for monster_id, entry in monster_map.items():
        monster_name = entry.name('en') # used for error display

        monster = db.Monster(id=entry.id, size=entry['size'])

        # Save basic weakness summary data
        if 'weaknesses' in entry and entry['weaknesses']:
            monster.has_weakness = True
            weaknesses = entry['weaknesses']
            for key, value in weaknesses['normal'].items():
                setattr(monster, 'weakness_'+key, value)

            if 'alt' in weaknesses:
                monster.has_alt_weakness = True
                for key, value in weaknesses['normal'].items():
                    setattr(monster, 'alt_weakness_'+key, value)

        # Save language data
        for language in supported_languages:
            alt_state_description = None
            if 'alt_description' in entry.get('weaknesses', {}):
                alt_state_description = entry['weaknesses']['alt_description'][language]

            monster.translations.append(db.MonsterText(
                lang_id=language,
                name=entry.name(language),
                description=entry['description'][language],
                alt_state_description=alt_state_description
            ))

        # Save hitzones
        for hitzone_data in entry.get('hitzones', []):
            hitzone = db.MonsterHitzone(
                cut=hitzone_data['cut'],
                impact=hitzone_data['impact'],
                shot=hitzone_data['shot'],
                fire=hitzone_data['fire'],
                water=hitzone_data['water'],
                thunder=hitzone_data['thunder'],
                dragon=hitzone_data['dragon'],
                ko=hitzone_data['ko'])

            for lang, part_name in hitzone_data['hitzone'].items():
                hitzone.translations.append(db.MonsterHitzoneText(
                    lang_id=lang,
                    hitzone_name=part_name
                ))

            monster.hitzones.append(hitzone)

        # Save breaks
        for break_data in entry.get('breaks', []):
            breakzone = db.MonsterBreak(
                flinch=break_data['flinch'],
                wound=break_data['wound'],
                sever=break_data['sever'],
                extract=break_data['extract']
            )
                        
            for lang, part_name in break_data['part'].items():
                breakzone.translations.append(db.MonsterBreakText(
                    lang_id=lang,
                    part_name=part_name
                ))

            monster.breaks.append(breakzone)

        # Create a temp base map of the conditions
        # This temp map extends the global map with monster-specific conditions
        #monster_conditions = DataMap(reward_conditions_map)
        #monster_conditions.extend(entry.get('break_conditions', []))

        # Save hunting rewards
        for reward in entry.get('rewards', []):
            condition_en = reward['condition_en']
            rank = reward['rank']
            item_name = reward['item_en']

            condition_id = monster_reward_conditions_map.id_of('en', condition_en)
            ensure(condition_id, f"Condition {condition_en} in monster {monster_name} does not exist")

            item_id = item_map.id_of('en', item_name)
            ensure(item_id, f"item reward {item_name} in monster {monster_name} does not exist")

            monster.rewards.append(db.MonsterReward(
                condition_id=condition_id,
                rank=rank,
                item_id=item_id,
                stack=reward['stack'],
                percentage=reward['percentage']
            ))

        # Save Habitats
        for location_name, habitat_values in entry.get('habitats', {}).items():
            location_id = location_map.id_of("en", location_name)
            ensure(location_id, "Invalid location name " + location_name)

            monster.habitats.append(db.MonsterHabitat(
                location_id=location_id,
                **habitat_values
            ))

        # Complete - add to session
        session.add(monster)

    print("Built Monsters")

def build_skills(session : sqlalchemy.orm.Session, mhdata):
    skill_map = mhdata.skill_map

    for id, entry in skill_map.items():
        skilltree = db.SkillTree(id=id)

        for language in supported_languages:
            skilltree.translations.append(db.SkillTreeText(
                lang_id=language,
                name=entry.name(language),
                description=entry['description'][language]
            ))

            for effect in entry['effects']:
                skilltree.skills.append(db.Skill(
                    lang_id=language,
                    level=effect['level'],
                    description=effect['description'][language]
                ))

        session.add(skilltree)
    
    print("Built Skills")

def build_armor(session : sqlalchemy.orm.Session, mhdata):
    item_map = mhdata.item_map
    skill_map = mhdata.skill_map
    armorset_map = mhdata.armorset_map
    armor_map = mhdata.armor_map

    # Write entries for armor sets  first
    for set_id, entry in armorset_map.items():
        armor_set = db.ArmorSet(id=set_id) 
        for language in supported_languages:
            armor_set.translations.append(db.ArmorSetText(
                lang_id=language,
                name=entry.name(language)
            ))
        session.add(armor_set)

    for armor_id, entry in armor_map.items():
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
                skilltree_id=skill_id,
                level=level
            ))
        
        # Armor Crafting
        for item, quantity in entry['craft'].items():
            item_id = item_map.id_of('en', item)
            ensure(item_id, f"Item {item} in Armor {armor_name_en} does not exist")
            
            armor.craft_items.append(db.ArmorRecipe(
                item_id=item_id,
                quantity=quantity
            ))

        session.add(armor)

    print("Built Armor")

def build_weapons(session : sqlalchemy.orm.Session, mhdata):
    item_map = mhdata.item_map
    weapon_data = mhdata.weapon_data
    weapon_map = mhdata.weapon_map

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

def build_decorations(session : sqlalchemy.orm.Session, mhdata):
    "Performs the build process for decorations. Must be done after skills"

    skill_map = mhdata.skill_map
    decoration_map = mhdata.decoration_map

    for decoration_id, entry in decoration_map.items():
        skill_id = skill_map.id_of('en', entry['skill_en'])
        ensure(skill_id, f"Decoration {entry.name('en')} refers to " +
            f"skill {entry['skill_en']}, which doesn't exist.")

        ensure("chances" in entry, "Missing chance data for " + entry.name('en'))
        
        decoration = db.Decoration(
            id=decoration_id,
            rarity=entry['rarity'],
            slot=entry['slot'],
            skilltree_id=skill_id,
            mysterious_feystone_chance=entry['chances']['mysterious_feystone_chance'],
            glowing_feystone_chance=entry['chances']['glowing_feystone_chance'],
            worn_feystone_chance=entry['chances']['worn_feystone_chance'],
            warped_feystone_chance=entry['chances']['warped_feystone_chance']
        )

        for language in supported_languages:
            decoration.translations.append(db.DecorationText(
                lang_id=language,
                name=entry.name('en')
            ))

        session.add(decoration)

    print("Built Decorations")

def build_charms(session : sqlalchemy.orm.Session, mhdata):
    item_map = mhdata.item_map
    skill_map = mhdata.skill_map
    charm_map = mhdata.charm_map

    for charm_id, entry in charm_map.items():
        charm = db.Charm(id=charm_id)

        for language in supported_languages:
            charm.translations.append(db.CharmText(
                lang_id=language,
                name=entry.name(language)
            ))

        for skill_en, level in entry['skills'].items():
            skill_id = skill_map.id_of('en', skill_en)
            ensure(skill_id, f"Charm {entry.name('en')} refers to " +
                f"item {skill_en}, which doesn't exist.")

            charm.skills.append(db.CharmSkill(
                skilltree_id=skill_id,
                level=level
            ))

        for item_en, quantity in entry['craft'].items():
            item_id = item_map.id_of('en', item_en)
            ensure(item_id, f"Charm {entry.name('en')} refers to " +
                f"item {item_en}, which doesn't exist.")

            charm.craft_items.append(db.CharmRecipe(
                item_id=item_id,
                quantity=quantity
            ))

        session.add(charm)

    print("Built Charms")
