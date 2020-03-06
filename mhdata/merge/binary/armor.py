from mhdata.io import create_writer, DataMap
from mhdata.load import load_data, schema, datafn
from mhdata.util import OrderedSet, bidict

from mhw_armor_edit.ftypes import am_dat, eq_crt, arm_up, skl_pt_dat
from mhdata.binary import ArmorCollection
from mhdata.binary.load import load_schema, load_text, SkillTextHandler
from .items import ItemUpdater
from .util import convert_recipe

from mhdata import cfg

from . import artifacts

# Index based gender restriction
gender_list = [None, 'male', 'female', 'both']

def update_armor(mhdata, item_updater: ItemUpdater, armor_collection: ArmorCollection):
    "Populates and updates armor information using the armorset_base as a source of truth"
    
    armor_series = armor_collection.armor

    # Get number of times armor can be upgraded by rarity level.
    # The first is max level pre-augment, the second is max post-augment
    # Thanks to the MHWorld Modders for the above info
    rarity_upgrades = {}
    for entry in load_schema(arm_up.ArmUp, "common/equip/arm_upgrade.arm_up").entries:
        rarity_upgrades[entry.index + 1] = (entry.unk10 - 1, entry.unk11 - 1)
    
    print("Binary armor data loaded")
    
    print("Writing list of armorset names (in order) to artifacts")
    artifacts.write_names_artifact('setnames.txt', [s.name['en'] for s in armor_series.values()])

    # Will store results. Language lookup and validation will be in english
    new_armorset_map = DataMap(languages="en", start_id=mhdata.armorset_map.max_id+1)
    new_armor_map = DataMap(languages="en", start_id=mhdata.armor_map.max_id+1)
    new_armorset_bonus_map = DataMap(languages="en")
    
    # Temporary storage for later processes
    all_set_skill_ids = OrderedSet()
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
                if not existing_armor:
                    print(f"Error: Invalid entry {armor_name}, does not exist in current DB nor is it in armor data")
                    continue
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
            skills = armor_data.skills + ([(None, None)] * (2 - len(armor_data.skills)))
            for i, (skill_id, skill_lvl) in enumerate(skills):
                if skill_id is None:
                    new_data['skills'][f'skill{i+1}_name'] = None
                    new_data['skills'][f'skill{i+1}_level'] = None
                else:
                    name_en = skill_text_handler.get_skilltree_name(skill_id)['en']
                    new_data['skills'][f'skill{i+1}_name'] = name_en
                    new_data['skills'][f'skill{i+1}_level'] = skill_lvl

            # Add recipe to new armor data. Also tracks the encounter.
            new_data['craft'] = convert_recipe(item_updater, armor_data.craft)

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


def update_charms(mhdata, item_updater: ItemUpdater, armor_collection: ArmorCollection):
    "Populates and updates charm information using the charm_base as a source of truth"

    print("Writing list of charm names (in order) to artifacts")
    def get_charm_raw(c):
        return {
            'name_en': c.name['en'],
            'parent': c.parent and c.parent.name['en']
        }
    artifacts.write_dicts_artifact('charms_raw.txt', [get_charm_raw(c) for c in armor_collection.charms])

    skill_text_handler = SkillTextHandler()
    charm_by_name = { c.name['en']:c for c in armor_collection.charms }
    
    new_charm_map = DataMap(languages=["en"])
    for charm_entry in mhdata.charm_map.values():
        new_charm_entry = { **charm_entry }

        data = charm_by_name.get(charm_entry['name_en'])
        if not data:
            print(f"Warning: Charm {charm_entry['name_en']} has no associated binary data")
            new_charm_map.insert(new_charm_entry)
            continue

        new_charm_entry['previous_en'] = data.parent and data.parent.name['en']
        new_charm_entry['rarity'] = data.rarity

        # Add skills to new armor data
        skills = data.skills + ([(None, None)] * (2 - len(data.skills)))
        for i, (skill_id, skill_lvl) in enumerate(skills):
            if skill_id is None:
                new_charm_entry[f'skill{i+1}_name'] = None
                new_charm_entry[f'skill{i+1}_level'] = None
            else:
                name_en = skill_text_handler.get_skilltree_name(skill_id)['en']
                new_charm_entry[f'skill{i+1}_name'] = name_en
                new_charm_entry[f'skill{i+1}_level'] = skill_lvl

        new_charm_entry['craft'] = []
        recipes = [('Create', data.craft), ('Upgrade', data.upgrade)]
        for rtype, recipe in recipes:
            if recipe:
                new_charm_entry['craft'].append({
                    'type': rtype,
                    **convert_recipe(item_updater, recipe)
                })

        new_charm_map.insert(new_charm_entry)

    # Write new data
    writer = create_writer()

    writer.save_base_map_csv(
        'charms/charm_base.csv', 
        new_charm_map, 
        translation_filename="charms/charm_base_translations.csv", 
        schema=schema.CharmBaseSchema()
    )

    writer.save_data_csv(
        "charms/charm_craft.csv",
        new_charm_map,
        key="craft"
    )

    print("Charm files updated\n")