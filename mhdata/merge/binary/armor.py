from mhdata.io import create_writer, DataMap
from mhdata.load import load_data, schema
from mhdata.util import OrderedSet, bidict
from mhdata.build import datafn

from mhw_armor_edit.ftypes import am_dat, eq_crt, arm_up, skl_pt_dat
from .load import load_schema, load_text, ItemTextHandler, convert_recipe
from .items import add_missing_items

# Index based gender restriction
gender_list = [None, 'male', 'female', 'both']

def update_armor():
    "Populates and updates armor information using the armorset_base as a source of truth"
    
    armor_text = load_text("common/text/steam/armor")
    armorset_text = load_text("common/text/steam/armor_series")

    # Parses binary armor data, mapped by the english name
    armor_data = {}    
    for armor_entry in load_schema(am_dat.AmDat, "common/equip/armor.am_dat").entries:
        if armor_entry.gender == 0: continue
        if armor_entry.order == 0: continue
        name_en = armor_text[armor_entry.gmd_name_index]['en']
        armor_data[name_en] = armor_entry

    # Parses craft data, mapped by the binary armor id
    armor_craft_data = {}
    for craft_entry in load_schema(eq_crt.EqCrt, "common/equip/armor.eq_crt").entries:
        armor_craft_data[craft_entry.equip_id] = craft_entry

    # Get number of times armor can be upgraded by rarity level.
    # Unk7 is max level pre-augment, Unk8 is max post-augment
    # Thanks to the MHWorld Modders for the above info
    rarity_upgrades = {}
    for entry in load_schema(arm_up.ArmUp, "common/equip/arm_upgrade.arm_up").entries:
        rarity_upgrades[entry.index + 1] = (entry.unk7 - 1, entry.unk8 - 1)

    # Get mapping from skill idx -> skill name en (as a bidict).
    # Discovered formula via inspecting mhw_armor_edit's source.
    skill_map = bidict()
    skill_text = load_text("common/text/vfont/skill_pt")
    for entry in load_schema(skl_pt_dat.SklPtDat, "common/equip/skill_point_data.skl_pt_dat").entries:
        skill_map[entry.index] = skill_text[entry.index * 3]['en']
    
    print("Binary data loaded")

    mhdata = load_data()
    print("Existing Data loaded. Using existing armorset data to drive new armor data.")

    # Will store results. Language lookup and validation will be in english
    new_armor_map = DataMap(languages="en")
    new_armorset_bonus_map = DataMap(languages="en")

    # Temporary storage for later processes
    all_set_skill_ids = OrderedSet()

    item_text_handler = ItemTextHandler()

    print("Populating armor data, keyed by the armorset data")
    next_armor_id = mhdata.armor_map.max_id + 1
    for armorset in mhdata.armorset_map.values():
        # Handle armor pieces
        for part, armor_name in datafn.iter_armorset_pieces(armorset):
            existing_armor = mhdata.armor_map.entry_of('en', armor_name)
            armor_binary = armor_data.get(armor_name)

            if not armor_binary:
                raise Exception(f"Failed to find binary armor data for {armor_name}")

            if armor_binary.set_skill1_lvl > 0:
                all_set_skill_ids.add(armor_binary.set_skill1)

            rarity = armor_binary.rarity + 1
            name_dict = armor_text[armor_binary.gmd_name_index]

            # Initial new armor data
            new_data = {
                'name': name_dict, # Override for translation support!
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

            # Add skills to new armor data
            for i in range(1, 2+1):
                skill_lvl = getattr(armor_binary, f"skill{i}_lvl")
                if skill_lvl != 0:
                    skill_id = getattr(armor_binary, f"skill{i}")
                    new_data['skills'][f'skill{i}_name'] = skill_map[skill_id]
                    new_data['skills'][f'skill{i}_pts'] = skill_lvl
                else:
                    new_data['skills'][f'skill{i}_name'] = None
                    new_data['skills'][f'skill{i}_pts'] = None

            # Add recipe to new armor data. Also track the encounter.
            recipe_binary = armor_craft_data[armor_binary.id]
            new_data['craft'] = convert_recipe(item_text_handler, recipe_binary)

            armor_entry = None
            if not existing_armor:
                print(f"Entry for {armor_name} not in armor map, creating new entry")
                armor_entry = new_armor_map.add_entry(next_armor_id, new_data)
                next_armor_id += 1

            else:
                armor_entry = new_armor_map.add_entry(existing_armor.id, {
                    **existing_armor,
                    **new_data
                })

    # Process set skills. As we don't currently understand the set -> skill map, we only translate
    for bonus_entry in mhdata.armorset_bonus_map.values():
        set_skill_idx = skill_map.reverse()[bonus_entry.name('en')]
        name_dict = skill_text[set_skill_idx * 3]
        new_armorset_bonus_map.insert({ **bonus_entry, 'name': name_dict })

    # Write new data
    writer = create_writer()

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