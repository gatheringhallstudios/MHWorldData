import sqlalchemy.orm
from sqlalchemy import func
import mhdata.sql as db

from mhdata import cfg
from mhdata.io import DataMap
from mhdata.util import ensure, ensure_warn, get_duplicates
from mhdata.load import datafn

from .objectindex import ObjectIndex
from .itemtracker import ItemTracker

def get_translated(obj, attr, lang):
    if attr not in obj:
        return None
    value = obj[attr].get(lang, None)
    return value or obj[attr]['en']

def calculate_next_recipe_id(session):
    current_max = session.query(func.max(db.RecipeItem.recipe_id)).scalar() 
    if not current_max:
        return 1
    return current_max + 1

def build_sql_database(output_filename, mhdata):
    "Builds a SQLite database and outputs to output_filename"
    sessionbuilder = db.recreate_database(output_filename)

    with db.session_scope(sessionbuilder) as session:
        # Add languages before starting the build
        for language in cfg.supported_languages:
            session.add(db.Language(
                id=language,
                name=cfg.all_languages[language],
                is_complete=(language not in cfg.incomplete_languages)
            ))

        # Create object used for detecting if an item is unmapped
        item_tracker = ItemTracker(mhdata)

        # Build the individual components
        # These functions are defined lower down in the file
        build_items(session, mhdata, item_tracker)
        build_locations(session, mhdata, item_tracker)
        build_monsters(session, mhdata, item_tracker)
        build_skills(session, mhdata)
        build_armor(session, mhdata)
        build_weapons(session, mhdata)
        build_kinsects(session, mhdata)
        build_decorations(session, mhdata)
        build_charms(session, mhdata)
        build_quests(session, mhdata, item_tracker)

        item_tracker.print_unmarked()
        
    print("Finished build")


def build_items(session : sqlalchemy.orm.Session, mhdata, item_tracker: ItemTracker):
    # Save basic item data first
    for entry in mhdata.item_map.values():
        item = db.Item(id=entry.id)
        item.category = entry['category']
        item.subcategory = entry['subcategory']
        item.rarity = entry['rarity'] or 0
        item.buy_price = entry['buy_price'] or 0
        item.sell_price = entry['sell_price'] or 0
        item.carry_limit = entry['carry_limit'] or 0
        item.points = entry['points'] or 0
        item.icon_name = entry['icon_name']
        item.icon_color = entry['icon_color']

        for language in cfg.supported_languages:
            item.translations.append(db.ItemText(
                lang_id=language,
                name=get_translated(entry, 'name', language),
                description=get_translated(entry, 'description', language),
            ))

        session.add(item)

    # Now save item combination data
    for entry in mhdata.item_combinations:
        result_id = mhdata.item_map.id_of('en', entry['result'])
        item_tracker.mark_encountered_id(result_id)

        session.add(db.ItemCombination(
            id=entry['id'],
            result_id=result_id,
            first_id=mhdata.item_map.id_of('en', entry['first']),
            second_id=mhdata.item_map.id_of('en', entry['second']),
            quantity=entry['quantity']
        ))
    
    print("Built Items")

def build_locations(session : sqlalchemy.orm.Session, mhdata, item_tracker: ItemTracker):
    for order_id, entry in enumerate(mhdata.location_map.values()):
        location_name = entry['name']['en']

        for language in cfg.supported_languages:
            session.add(db.Location(
                id=entry.id,
                order_id=order_id,
                lang_id=language,
                name=get_translated(entry, 'name', language),
            ))

        for item_entry in entry['items']:
            item_lang = item_entry['item_lang']
            item_name = item_entry['item']
            item_id = mhdata.item_map.id_of(item_lang, item_name)

            item_tracker.mark_encountered_id(item_id)

            session.add(db.LocationItem(
                location_id=entry.id,
                area=item_entry['area'],
                rank=item_entry['rank'],
                item_id=item_id,
                stack=item_entry['stack'],
                percentage=item_entry['percentage'],
                nodes=item_entry['nodes']
            ))

        for camp in entry['camps']:
            for language in cfg.supported_languages:
                session.add(db.LocationCamp(
                    location_id=entry.id,
                    lang_id = language,
                    name = get_translated(camp, 'name', language),
                    area = camp['area']
                ))
            
    print("Built locations")

def build_monsters(session : sqlalchemy.orm.Session, mhdata, item_tracker: ItemTracker):
    item_map = mhdata.item_map
    location_map = mhdata.location_map
    monster_map = mhdata.monster_map
    monster_reward_conditions_map = mhdata.monster_reward_conditions_map

    # Save conditions first
    for condition_id, entry in monster_reward_conditions_map.items():
        for language in cfg.supported_languages:
            session.add(db.MonsterRewardConditionText(
                id=condition_id,
                lang_id=language,
                name=get_translated(entry, 'name', language),
            ))

    # Save monsters
    for order_id, entry in enumerate(monster_map.values()):
        monster = db.Monster(
            id=entry.id,
            order_id=order_id,
            size=entry['size'],
            pitfall_trap=entry['pitfall_trap'],
            shock_trap=entry['shock_trap'],
            vine_trap=entry['vine_trap']
        )
        
        # todo: refactor to allow translations. Currently set when weaknesses are read
        alt_state_description = None

        # Save basic weakness summary data
        if 'weaknesses' in entry and entry['weaknesses']:
            elements = [
                'fire', 'water', 'ice', 'thunder', 'dragon', 
                'poison', 'sleep', 'paralysis', 'blast', 'stun']

            weaknesses = { e['form']:e for e in entry['weaknesses'] }
            form_normal = weaknesses.get('normal')
            form_alt = weaknesses.get('alt')

            invalid_keys = [k for k in weaknesses.keys() if k not in ('normal', 'alt')]
            if invalid_keys:
                raise Exception(f"Monster {entry.name('en')} has invalid form(s) {', '.join(invalid_keys)}")

            if form_normal:
                monster.has_weakness = True
                for element in elements:
                    setattr(monster, 'weakness_'+element, form_normal[element])

            if form_alt:
                monster.has_alt_weakness = True
                alt_state_description = form_alt['alt_description']

                for element in elements:
                    value = form_alt[element]
                    if value is None:
                        value = form_normal[element]
                    setattr(monster, 'alt_weakness_'+element, value)

        # Save language data
        for language in cfg.supported_languages:
            monster.translations.append(db.MonsterText(
                lang_id=language,
                name=get_translated(entry, 'name', language),
                ecology=entry['ecology_en'],
                description=get_translated(entry, 'description', language),
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
                ice=hitzone_data['ice'],
                dragon=hitzone_data['dragon'],
                ko=hitzone_data['ko'])

            for language in cfg.supported_languages:
                part_name = get_translated(hitzone_data, 'hitzone', language)
                hitzone.translations.append(db.MonsterHitzoneText(
                    lang_id=language,
                    name=part_name
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

            for language in cfg.supported_languages:
                breakzone.translations.append(db.MonsterBreakText(
                    lang_id=language,
                    part_name=get_translated(break_data, 'part', language),
                ))

            monster.breaks.append(breakzone)

        # Save ailments
        ailments = entry.get('ailments', None)
        if ailments:
            monster.ailment_roar = ailments['roar']
            monster.ailment_wind = ailments['wind']
            monster.ailment_tremor = ailments['tremor']
            monster.ailment_defensedown = ailments['defense_down']
            monster.ailment_fireblight = ailments['fireblight']
            monster.ailment_waterblight = ailments['waterblight']
            monster.ailment_thunderblight = ailments['thunderblight']
            monster.ailment_iceblight = ailments['iceblight']
            monster.ailment_dragonblight = ailments['dragonblight']
            monster.ailment_blastblight = ailments['blastblight']
            monster.ailment_poison = ailments['poison']
            monster.ailment_sleep = ailments['sleep']
            monster.ailment_paralysis = ailments['paralysis']
            monster.ailment_bleed = ailments['bleed']
            monster.ailment_stun = ailments['stun']
            monster.ailment_mud = ailments['mud']
            monster.ailment_effluvia = ailments['effluvia']

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
            item_id = item_map.id_of('en', item_name)

            item_tracker.mark_encountered_id(item_id)

            monster.rewards.append(db.MonsterReward(
                condition_id=condition_id,
                rank=rank,
                item_id=item_id,
                stack=reward['stack'],
                percentage=reward['percentage'] or 0
            ))

        # Save Habitats
        for habitat_data in entry.get('habitats', []):
            location_name = habitat_data['map_en']
            location_id = location_map.id_of("en", location_name)
            ensure(location_id, "Invalid location name " + location_name)

            monster.habitats.append(db.MonsterHabitat(
                location_id=location_id,
                start_area=habitat_data['start_area'],
                move_area=habitat_data['move_area'],
                rest_area=habitat_data['rest_area']
            ))

        # Complete - add to session
        session.add(monster)

    print("Built Monsters")

def build_skills(session : sqlalchemy.orm.Session, mhdata):
    skill_map = mhdata.skill_map

    for skill_entry in skill_map.values():
        skilltree = db.SkillTree(
            id=skill_entry.id,
            max_level=len(skill_entry['levels']),
            icon_color=skill_entry['icon_color'],
            secret=skill_entry['secret'] or 0,
            unlocks_id=skill_map.id_of('en', skill_entry['unlocks']))

        for language in cfg.supported_languages:
            skilltree.translations.append(db.SkillTreeText(
                lang_id=language,
                name=get_translated(skill_entry, 'name', language),
                description=get_translated(skill_entry, 'description', language)
            ))

            for effect in skill_entry['levels']:
                skilltree.skills.append(db.Skill(
                    lang_id=language,
                    level=effect['level'],
                    description=get_translated(effect, 'description', language)
                ))

        session.add(skilltree)
    
    print("Built Skills")

def build_armor(session : sqlalchemy.orm.Session, mhdata):
    item_map = mhdata.item_map
    skill_map = mhdata.skill_map
    armorset_map = mhdata.armorset_map
    armorset_bonus_map = mhdata.armorset_bonus_map
    armor_map = mhdata.armor_map

    # Create reverse mapping. In SQL, armor links to armorset instead
    armor_to_armorset = {}
    armorset_to_bonus = {}

    # Write entries from armor set bonuses
    # These are written first as they are "linked to"
    for bonus_entry in armorset_bonus_map.values():
        for language in cfg.supported_languages:
            session.add(db.ArmorSetBonusText(
                id=bonus_entry.id,
                lang_id=language,
                name=get_translated(bonus_entry, 'name', language)
            ))
        
        for skill_name, required in datafn.iter_setbonus_skills(bonus_entry):
            skill_id = skill_map.id_of('en', skill_name)
            session.add(db.ArmorSetBonusSkill(
                setbonus_id=bonus_entry.id,
                skilltree_id=skill_id,
                required=required
            ))

    # Write entries for armor sets
    for set_id, entry in armorset_map.items():
        armorset_bonus_id = None

        if entry['bonus']:
            armorset_bonus_id = armorset_bonus_map.id_of('en', entry['bonus'])
            ensure(armorset_bonus_id, f"Armorset bonus {entry['bonus']} in armorsets doesn't exist")
            armorset_to_bonus[set_id] = armorset_bonus_id

        armorset = db.ArmorSet(
            id=set_id,
            rank=entry['rank'],
            armorset_bonus_id=armorset_bonus_id
        ) 

        if entry['monster']:
            armorset.monster_id = mhdata.monster_map.id_of('en', entry['monster'])
        
        for language in cfg.supported_languages:
            armorset.translations.append(db.ArmorSetText(
                lang_id=language,
                name=get_translated(entry, 'name', language)
            ))

        session.add(armorset)

        # Populate reverse map (to allow armor to link to armorset)
        for part in cfg.armor_parts:
            if not entry[part]:
                continue
            
            armor_reverse_id = mhdata.armor_map.id_of('en', entry[part])
            armor_to_armorset[armor_reverse_id] = set_id

    # Store recipe id to start from for armor
    next_recipe_id = calculate_next_recipe_id(session)

    # Write entries for armor
    for order_id, entry in enumerate(armor_map.values()):
        armor_name_en = entry.name('en')

        armor = db.Armor(id = entry.id)
        armor.order_id = order_id
        armor.rarity = entry['rarity']
        armor.armor_type = entry['type']
        armor.male = entry['gender'] in ('male', 'both')
        armor.female = entry['gender'] in ('female', 'both')
        armor.slot_1 = entry['slot_1']
        armor.slot_2 = entry['slot_2']
        armor.slot_3 = entry['slot_3']
        armor.defense_base = entry['defense_base']
        armor.defense_max = entry['defense_max']
        armor.defense_augment_max = entry['defense_augment_max']
        armor.fire = entry['defense_fire']
        armor.water = entry['defense_water']
        armor.thunder = entry['defense_thunder']
        armor.ice = entry['defense_ice']
        armor.dragon = entry['defense_dragon']

        armorset_id = armor_to_armorset.get(entry.id, None)
        armorset_entry = armorset_map[armorset_id]
        armor.rank = armorset_entry['rank']
        armor.armorset_id = armorset_id
        armor.armorset_bonus_id = armorset_to_bonus.get(armorset_id, None)

        for language in cfg.supported_languages:
            armor.translations.append(db.ArmorText(
                lang_id=language, 
                name=get_translated(entry, 'name', language),
            ))

        # Armor Skills
        for skill, level in datafn.iter_skill_levels(entry['skills']):
            skill_id = skill_map.id_of('en', skill)
            armor.skills.append(db.ArmorSkill(
                skilltree_id=skill_id,
                level=level
            ))

        # Armor Crafting
        for item_name, quantity in datafn.iter_armor_recipe(entry):
            item_id = item_map.id_of('en', item_name)
            armor.craft_items.append(db.RecipeItem(
                recipe_id=next_recipe_id,
                item_id=item_id,
                quantity=quantity
            ))

        next_recipe_id += 1

        session.add(armor)

    print("Built Armor")

def build_weapons(session : sqlalchemy.orm.Session, mhdata):
    item_map = mhdata.item_map
    weapon_map = mhdata.weapon_map

    # Save all weapon ammo configurations
    for entry in mhdata.weapon_ammo_map.values():
        ammo = db.WeaponAmmo(
            id=entry.id,
            deviation=entry['deviation'],
            special_ammo=entry['special']
        )

        # helper to assign the entirety of a group to the db
        def assign_group(ammotype):
            group = entry[ammotype]
            setattr(ammo, ammotype + "_clip", group['clip'])
            setattr(ammo, ammotype + "_rapid", group['rapid'])
            setattr(ammo, ammotype + "_recoil", group.get('recoil', None) or 0)
            setattr(ammo, ammotype + "_reload", group.get('reload', None))

        assign_group('normal1')
        assign_group('normal2')
        assign_group('normal3')
        assign_group('pierce1')
        assign_group('pierce2')
        assign_group('pierce3')
        assign_group('spread1')
        assign_group('spread2')
        assign_group('spread3')
        assign_group('sticky1')
        assign_group('sticky2')
        assign_group('sticky3')
        assign_group('cluster1')
        assign_group('cluster2')
        assign_group('recover1')
        assign_group('recover2')
        assign_group('poison1')
        assign_group('poison2')
        assign_group('paralysis1')
        assign_group('paralysis2')
        assign_group('sleep1')
        assign_group('sleep2')
        assign_group('exhaust1')
        assign_group('exhaust2')
        assign_group('flaming')
        assign_group('water')
        assign_group('freeze')
        assign_group('thunder')
        assign_group('dragon')

        assign_group('slicing')
        assign_group('demon')
        assign_group('armor')
        assign_group('tranq')
        
        ammo.wyvern_clip = entry['wyvern']['clip']
        ammo.wyvern_reload = entry['wyvern']['reload']

        session.add(ammo)

    # Save all weapon melodies
    # The SQL format was for an older format where the same melody linked to multiple notes.
    # A refactor will be required at some point to separate melody and the notes to play said melody.
    # However, that is a breaking change, so we show a warning for now.
    print("Warning: Weapon Melody SQL format will change in future updates")
    for melody_entry in mhdata.weapon_melodies.values():
        for note_entry in melody_entry['notes']:  
            melody = db.WeaponMelody(
                notes=note_entry['notes'],
                duration=melody_entry['duration'],
                extension=melody_entry['extension']
            )

            for language in cfg.supported_languages:
                melody.translations.append(db.WeaponMelodyText(
                    lang_id=language,
                    effect1=get_translated(melody_entry, 'effect1', language),
                    effect2=get_translated(melody_entry, 'effect2', language)
                ))

            session.add(melody)

    # Prepass to determine which weapons are "final"
    # All items that are a previous to another are "not final"
    all_final = set(weapon_map.keys())
    for entry in weapon_map.values():
        if not entry.get('previous_en', None):
            continue
        try:
            prev_id = weapon_map.id_of('en', entry['previous_en'], entry['weapon_type'])
            all_final.remove(prev_id)
        except KeyError:
            pass

    # Query next recipe id beforehand
    next_recipe_id = calculate_next_recipe_id(session)

    # now iterate over actual weapons
    for idx, entry in enumerate(weapon_map.values()):
        weapon_id = entry.id
        weapon_type = entry['weapon_type']

        weapon = db.Weapon(
            id=weapon_id,
            order_id=idx,
            weapon_type=weapon_type,
        )
        
        # Add language translations
        for language in cfg.supported_languages:
            weapon.translations.append(db.WeaponText(
                lang_id=language,
                name=get_translated(entry, 'name', language)
            ))

        weapon.category = entry['category']
        weapon.rarity = entry['rarity']
        weapon.attack = entry['attack']
        weapon.attack_true = int(entry['attack'] / cfg.weapon_multiplier[weapon_type])
        weapon.affinity = entry['affinity']
        weapon.defense = entry['defense'] or 0
        weapon.slot_1 = entry['slot_1']
        weapon.slot_2 = entry['slot_2']
        weapon.slot_3 = entry['slot_3']

        weapon.element1 = entry['element1']
        weapon.element1_attack = entry['element1_attack']
        weapon.element2 = entry['element2']
        weapon.element2_attack = entry['element2_attack']
        weapon.element_hidden = entry['element_hidden']
        weapon.elderseal = entry['elderseal']

        if entry.get('sharpness', None):
            weapon.sharpness = datafn.merge_sharpness(entry)
            weapon.sharpness_maxed = entry['sharpness']['maxed']

        weapon.kinsect_bonus = entry['kinsect_bonus']
        weapon.phial = entry['phial']
        weapon.phial_power = entry['phial_power']
        weapon.shelling = entry['shelling']
        weapon.shelling_level = entry['shelling_level']
        weapon.notes = entry['notes']

        weapon.craftable = False # set to true later if it can be crafted
        weapon.final = weapon_id in all_final

        previous_weapon_name = entry.get('previous_en', None)
        if previous_weapon_name:
            previous_weapon_id = weapon_map.id_of("en", previous_weapon_name, weapon_type)
            ensure(previous_weapon_id, f"Weapon {previous_weapon_name} does not exist")
            weapon.previous_weapon_id = previous_weapon_id

        # Add crafting/upgrade recipes
        for recipe in entry.get('craft', {}):
            recipe_type = recipe['type']
            if recipe_type == "Create":
                weapon.craftable = True
                weapon.create_recipe_id = next_recipe_id
            else:
                weapon.upgrade_recipe_id = next_recipe_id
                
            for item, quantity in datafn.iter_recipe(recipe):
                item_id = item_map.id_of("en", item)
                session.add(db.RecipeItem(
                    recipe_id=next_recipe_id,
                    item_id=item_id,
                    quantity=quantity
                ))

            next_recipe_id += 1

        # Bow data (if any)
        if entry.get("bow", None):
            bow_data = entry['bow']
            weapon.coating_close = bow_data['close']
            weapon.coating_power = bow_data['power']
            weapon.coating_poison = bow_data['poison']
            weapon.coating_paralysis = bow_data['paralysis']
            weapon.coating_sleep = bow_data['sleep']
            weapon.coating_blast = bow_data['blast']

        # Gun data mapping (if any)
        ammo_config_name = entry.get('ammo_config', None)
        if ammo_config_name:
            weapon.ammo_id = mhdata.weapon_ammo_map[ammo_config_name].id
        
        # Skills
        if entry['skill']:
            skill_id = mhdata.skill_map.id_of('en', entry['skill'])
            weapon.skills.append(db.WeaponSkill(
                skilltree_id=skill_id,
                level=1
            ))

        session.add(weapon)

    print("Built Weapons")

def build_kinsects(session: sqlalchemy.orm.Session, mhdata):
    # Prepass to determine which entries are "final"
    # Those that are a previous to another are "not final"
    all_final = set(mhdata.kinsect_map.keys())
    for entry in mhdata.kinsect_map.values():
        if not entry.get('previous_en', None):
            continue
        try:
            prev_id = mhdata.kinsect_map.id_of('en', entry['previous_en'])
            all_final.remove(prev_id)
        except KeyError:
            pass

    # Store next recipe id ahead of time
    next_recipe_id = calculate_next_recipe_id(session)

    # Save kinsects
    for entry in mhdata.kinsect_map.values():
        kinsect = db.Kinsect(
            id=entry.id,
            rarity=entry['rarity'],
            previous_kinsect_id=mhdata.kinsect_map.id_of('en', entry['previous_en']),
            attack_type=entry['attack_type'],
            dust_effect=entry['dust_effect'],
            power=entry['power'],
            speed=entry['speed'],
            heal=entry['heal'],
            final= entry.id in all_final
        )
        
        # Add language translations
        for language in cfg.supported_languages:
            kinsect.translations.append(db.KinsectText(
                lang_id=language,
                name=get_translated(entry, 'name', language)
            ))

        # Save kinsect recipe
        recipe = entry.get('craft', None)
        if recipe:
            for item, quantity in datafn.iter_recipe(recipe):
                item_id = mhdata.item_map.id_of("en", item)
                ensure(item_id, f"Kinsect {entry.name('en')} refers to " +
                    f"item {item}, which doesn't exist.")
                kinsect.craft_items.append(db.RecipeItem(
                    recipe_id=next_recipe_id,
                    item_id=item_id,
                    quantity=quantity
                ))
            next_recipe_id += 1

        session.add(kinsect)

    print("Built Kinsects")

def build_decorations(session : sqlalchemy.orm.Session, mhdata):
    "Performs the build process for decorations. Must be done after skills"

    skill_map = mhdata.skill_map
    decoration_map = mhdata.decoration_map

    for decoration_id, entry in decoration_map.items():
        skills = list(datafn.iter_skill_levels(entry, amount=2, pad=True))
        ensure("chances" in entry, "Missing chance data for " + entry.name('en'))
        
        decoration = db.Decoration(
            id=decoration_id,
            rarity=entry['rarity'],
            slot=entry['slot'],
            icon_color=entry['icon_color'],
            skilltree_id=skill_map.id_of('en', skills[0][0]),
            skilltree_level=skills[0][1],
            skilltree2_id=skill_map.id_of('en', skills[1][0]),
            skilltree2_level=skills[1][1],
            mysterious_feystone_percent=entry['chances']['mysterious'],
            glowing_feystone_percent=entry['chances']['glowing'],
            worn_feystone_percent=entry['chances']['worn'],
            warped_feystone_percent=entry['chances']['warped'],
            ancient_feystone_percent=entry['chances']['ancient'],
            carved_feystone_percent=entry['chances']['carved'],
            sealed_feystone_percent=entry['chances']['sealed'],
        )

        for language in cfg.supported_languages:
            decoration.translations.append(db.DecorationText(
                lang_id=language,
                name=get_translated(entry, 'name', language)
            ))

        session.add(decoration)

    print("Built Decorations")

def build_charms(session : sqlalchemy.orm.Session, mhdata):
    item_map = mhdata.item_map
    skill_map = mhdata.skill_map
    charm_map = mhdata.charm_map

    # Store next recipe id ahead of time
    next_recipe_id = calculate_next_recipe_id(session)

    for order_id, entry in enumerate(charm_map.values()):
        # Note: previous is ok to be None
        previous = charm_map.id_of('en', entry['previous_en'])

        charm = db.Charm(
            id=entry.id,
            order_id=order_id,
            previous_id=previous,
            rarity=entry['rarity']
        )

        for language in cfg.supported_languages:
            charm.translations.append(db.CharmText(
                lang_id=language,
                name=entry.name(language)
            ))

        # Add charm skills
        for skill_en, level in datafn.iter_skill_levels(entry, amount=2):
            skill_id = skill_map.id_of('en', skill_en)
            ensure(skill_id, f"Charm {entry.name('en')} refers to " +
                f"skill {skill_en}, which doesn't exist.")

            charm.skills.append(db.CharmSkill(
                skilltree_id=skill_id,
                level=level
            ))

        # Add Charm Recipe
        if entry.get('craft'):
            for item_en, quantity in datafn.iter_recipe(entry['craft'][0]):
                item_id = item_map.id_of('en', item_en)
                ensure(item_id, f"Charm {entry.name('en')} refers to " +
                    f"item {item_en}, which doesn't exist.")

                charm.craft_items.append(db.RecipeItem(
                    recipe_id=next_recipe_id,
                    item_id=item_id,
                    quantity=quantity
                ))
            next_recipe_id += 1

        session.add(charm)

    print("Built Charms")


def build_quests(session : sqlalchemy.orm.Session, mhdata, item_tracker: ItemTracker):
    for order_id, entry in enumerate(mhdata.quest_map.values()):
        quest = db.Quest(
            id=entry.id,
            order_id=order_id,
            category=entry['category'],
            stars=entry['stars'],
            quest_type=entry['quest_type'],
            location_id=mhdata.location_map.id_of('en', entry['location_en']),
            zenny=entry['zenny']
        )

        for language in cfg.supported_languages:
            quest.translations.append(db.QuestText(
                lang_id=language,
                name=entry.name(language),
                objective=entry['objective'][language],
                description=entry['description'][language]
            ))

        for monster_entry in entry['monsters']:
            quest.monsters.append(db.QuestMonster(
                monster_id=mhdata.monster_map.id_of('en', monster_entry['monster_en']),
                quantity=monster_entry['quantity'],
                is_objective=monster_entry['is_objective']
            ))

        for reward_entry in entry['rewards']:
            item_id = mhdata.item_map.id_of('en', reward_entry['item_en'])
            item_tracker.mark_encountered_id(item_id)
            quest.rewards.append(db.QuestReward(
                group=reward_entry['group'],
                item_id=item_id,
                stack=reward_entry['stack'],
                percentage=reward_entry['percentage']
            ))

        session.add(quest)

    print('Build Quests')
