from os.path import abspath, join, dirname

from mhdata.io import DataMap, DataReaderWriter
from mhdata.load import load_data, cfg

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

def repair_armor_data():
    "Repairs all armor data to synchronize ordering"
    from . import repairarmor
    repairarmor.repair_armor_order(writer)
