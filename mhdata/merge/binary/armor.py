from mhdata.io import create_writer, DataMap
from mhdata.load import load_data, schema, datafn
from mhdata.util import OrderedSet, bidict

from mhw_armor_edit.ftypes import am_dat, eq_crt, arm_up, skl_pt_dat
from .load import load_schema, load_text, ItemTextHandler, SkillTextHandler, convert_recipe, load_armor_series
from .items import add_missing_items

from mhdata import cfg

from . import artifacts

# Index based gender restriction
gender_list = [None, 'male', 'female', 'both']

def update_armor():
    "Populates and updates armor information using the armorset_base as a source of truth"
    
    armor_series = load_armor_series()

    # Get number of times armor can be upgraded by rarity level.
    # Unk7 is max level pre-augment, Unk8 is max post-augment
    # Thanks to the MHWorld Modders for the above info
    rarity_upgrades = {}
    for entry in load_schema(arm_up.ArmUp, "common/equip/arm_upgrade.arm_up").entries:
        rarity_upgrades[entry.index + 1] = (entry.unk7 - 1, entry.unk8 - 1)
    
    print("Binary armor data loaded")

    mhdata = load_data()
    print("Existing Data loaded. Using existing armorset data to drive new armor data.")
    
    print("Writing list of armorset names (in order) to artifacts")
    artifacts.write_names_artifact('setnames.txt', [s.name['en'] for s in armor_series.values()])

    # Will store results. Language lookup and validation will be in english
    new_armorset_map = DataMap(languages="en", start_id=mhdata.armorset_map.max_id+1)
    new_armor_map = DataMap(languages="en", start_id=mhdata.armor_map.max_id+1)
    new_armorset_bonus_map = DataMap(languages="en")
    
    # Temporary storage for later processes
    all_set_skill_ids = OrderedSet()
    item_text_handler = ItemTextHandler()
    skill_text_handler = SkillTextHandler()
    armor_data_by_name = {}

    print("Updating set data, keyed by the existing names in armorset_base.csv")
    for armorset_entry in mhdata.armorset_map.values():
        armorseries_data = armor_series.get(armorset_entry.name('en'))
        if not armorseries_data:
            print(f"Armor series {armorset_entry.name('en')} doesn't exist in binary, skipping")
            new_armorset_map.insert(armorset_entry)
            continue

        new_entry = { **armorset_entry,
            'name': armorseries_data.name,
            'rank': armorseries_data.rank
        }

        first_armor = armorseries_data.armors[0].binary
        if first_armor.set_skill1_lvl > 0:
            skill_id = first_armor.set_skill1
            all_set_skill_ids.add(skill_id)
            new_entry['bonus'] = skill_text_handler.get_skilltree_name(skill_id)['en']

        for part in cfg.armor_parts:
            armor = armorseries_data.get_part(part)
            if armor:
                armor_data_by_name[armor.name['en']] = armor
                new_entry[part] = armor.name['en']
            else:
                new_entry[part] = None

        new_armorset_map.insert(new_entry)

    print("Armorset entries updated")

    print("Updating armor")
    for armorset_entry in new_armorset_map.values():
        # Handle armor pieces
        for part, armor_name in datafn.iter_armorset_pieces(armorset_entry):
            existing_armor = mhdata.armor_map.entry_of('en', armor_name)
            armor_data = armor_data_by_name.get(armor_name, None)

            if not armor_data:
                print(f"Failed to find binary armor data for {armor_name}, maintaining existing data")
                new_armor_map.insert(existing_armor)
                continue

            armor_binary = armor_data.binary
            rarity = armor_binary.rarity + 1

            # Initial new armor data
            new_data = {
                'name': armor_data.name,
                'rarity': rarity,
                'type': part,
                'gender': gender_list[armor_binary.gender],
                'slot_1': armor_binary.gem_slot1_lvl,
                'slot_2': armor_binary.gem_slot2_lvl,
                'slot_3': armor_binary.gem_slot3_lvl,
                'defense_base': armor_binary.defense,
                'defense_max': armor_binary.defense + rarity_upgrades[rarity][0] * 2,
                'defense_augment_max': armor_binary.defense + rarity_upgrades[rarity][1] * 2,
                'defense_fire': armor_binary.fire_res,
                'defense_water': armor_binary.water_res,
                'defense_thunder': armor_binary.thunder_res,
                'defense_ice': armor_binary.ice_res,
                'defense_dragon': armor_binary.dragon_res,
                'skills': {},
                'craft': {}
            }

            if existing_armor:
                new_data['id'] = existing_armor.id

            # Add skills to new armor data
            for i in range(1, 2+1):
                skill_lvl = getattr(armor_binary, f"skill{i}_lvl")
                if skill_lvl != 0:
                    skill_id = getattr(armor_binary, f"skill{i}")
                    name_en = skill_text_handler.get_skilltree_name(skill_id)['en']
                    new_data['skills'][f'skill{i}_name'] = name_en
                    new_data['skills'][f'skill{i}_pts'] = skill_lvl
                else:
                    new_data['skills'][f'skill{i}_name'] = None
                    new_data['skills'][f'skill{i}_pts'] = None

            # Add recipe to new armor data. Also track the encounter.
            recipe_binary = armor_data.recipe
            new_data['craft'] = convert_recipe(item_text_handler, recipe_binary)

            # Add new data to new armor map
            new_armor_map.insert(new_data)

    # Process set skills. As we don't currently understand the set -> skill map, we only translate
    # We pull the already established set skill name from existing CSV
    for bonus_entry in mhdata.armorset_bonus_map.values():
        skilltree = skill_text_handler.get_skilltree(bonus_entry.name('en'))
        name_dict = skill_text_handler.get_skilltree_name(skilltree.index)
        new_armorset_bonus_map.insert({ **bonus_entry, 'name': name_dict })

    # Write new data
    writer = create_writer()

    writer.save_base_map_csv(
        "armors/armorset_base.csv", 
        new_armorset_map, 
        schema=schema.ArmorSetSchema(),
        translation_filename="armors/armorset_base_translations.csv")

    writer.save_base_map_csv(
        "armors/armor_base.csv", 
        new_armor_map, 
        schema=schema.ArmorBaseSchema(),
        translation_filename="armors/armor_base_translations.csv")

    writer.save_data_csv(
        "armors/armor_skills_ext.csv",
        new_armor_map,
        key="skills"
    )

    writer.save_data_csv(
        "armors/armor_craft_ext.csv",
        new_armor_map,
        key="craft"
    )

    writer.save_base_map_csv(
        "armors/armorset_bonus_base.csv",
        new_armorset_bonus_map,
        schema=schema.ArmorSetBonus(),
        translation_filename="armors/armorset_bonus_base_translations.csv"
    )

    print("Armor files updated\n")

    add_missing_items(item_text_handler.encountered, mhdata=mhdata)