from os.path import abspath, join, dirname

from mhdata.io import DataMap, DataReaderWriter
from mhdata.io.csv import save_csv
from mhdata.load import load_data, cfg, schema

writer = DataReaderWriter(
    required_languages=cfg.required_languages,
    languages=cfg.supported_languages, 
    data_path=join(dirname(abspath(__file__)), '../../source_data/')
)

# Implementation commented out due to new structure
# uncomment it and remake it once we want to resort rewards.
# def repair_rewards():
#     data = load_data()
    
#     for monster_id, monster_entry in data.monster_map.items():
#         # If there are no rewards, skip
#         if 'rewards' not in monster_entry:
#             continue

#         old_rewards = monster_entry['rewards']

#         # Store all conditions for the monster here. 
#         # Any still here at the end print a warning
#         all_conditions = set(old_rewards.keys())

#         # add all results to this phase here
#         new_rewards = {}

#         # now iterate on the conditions map. We're trying to match the order
#         for condition_en in data.monster_reward_conditions_map.names('en'):
#             if condition_en not in old_rewards.keys():
#                 continue
#             new_rewards[condition_en] = old_rewards[condition_en]
#             all_conditions.remove(condition_en)

#         # Now add up all missing entries and show warnings
#         for condition_en in all_conditions:
#             new_rewards[condition_en] = old_rewards[condition_en]
#             print(f"WARNING: {condition_en} in monster {monster_entry.name('en')} is an invalid entry")

#         monster_entry['rewards'] = new_rewards

#     # Now save the output. The actual monsters will be reordered by this operation
#     writer.save_data_map('monsters/monster_rewards.json', data.monster_map, fields=['rewards'])
#     print("Repair complete")

def repair_skill_data():
    "Reorganizes skill data ordering to match base map"
    data = load_data()

    writer.save_data_csv(
        "skills/skill_levels.csv", 
        data.skill_map, 
        key="levels", 
        groups=['description'])

def repair_armor_data():
    data = load_data()

    armor_map = data.armor_map
    armorset_map = data.armorset_map

    new_armor_map = DataMap()

    # Copy all items in armorset order
    for set_entry in armorset_map.values():
        # All armor pieces in the set
        armor_names = [set_entry[part] for part in cfg.armor_parts]
        armor_names = list(filter(None, armor_names))

        armor_lang = set_entry['armor_lang']
        for armor_name in armor_names:
            armor_id = armor_map.id_of(armor_lang, armor_name)
            armor = armor_map.pop(armor_id)
            new_armor_map.insert(armor)

    # Copy over remaining items
    for remaining_item in armor_map:
        new_armor_map.insert(remaining_item)

    # Save results (todo: refactor, move to writer)
    armor_schema = schema.ArmorBaseSchema()
    result_list = new_armor_map.to_list()
    result, errors = armor_schema.dump(result_list, many=True)
    writer.save_csv("armors/armor_base.csv", result)

def repair_decoration_colors():
    data = load_data()

    for entry in data.decoration_map.values():
        skill_en = entry['skill_en']
        skill_entry = data.skill_map.entry_of("en", skill_en)
        entry['icon_color'] = skill_entry['icon_color']

    decoration_schema = schema.DecorationBaseSchema()
    result, errors = decoration_schema.dump(data.decoration_map.to_list(), many=True)
    writer.save_csv("decorations/decoration_base.csv", result)
