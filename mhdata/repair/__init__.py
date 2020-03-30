from os.path import abspath, join, dirname
from operator import itemgetter
from itertools import groupby

from mhdata import cfg
from mhdata.io import DataMap, DataReaderWriter, create_writer
from mhdata.io.csv import save_csv
from mhdata.load import load_data, schema

writer = create_writer()

def repair_rewards():
    data = load_data()

    for monster_id, monster_entry in data.monster_map.items():
        # If there are no rewards, skip
        if 'rewards' not in monster_entry:
            continue

        rewards_per_rank = [[] for x in range(len(cfg.supported_ranks))]

        # split into ranks first
        for idx, rank in enumerate(cfg.supported_ranks):
            for reward in monster_entry['rewards']:
                if reward['rank'].lower() == rank.lower():
                    rewards_per_rank[idx].append(reward)
        
        if sum(len(r) for r in rewards_per_rank) != len(monster_entry['rewards']):
            raise Exception("Not all rewards successfully split, some may not belong to the right rank")

        for idx, rewards in enumerate(rewards_per_rank):
            grouped_conditions = {}
            for r in rewards:
                grouped_conditions.setdefault(r['condition_en'], []).append(r)
            
            new_rewards = []
            for condition_entry in data.monster_reward_conditions_map.values():
                condition = condition_entry['name_en']
                if condition not in grouped_conditions:
                    continue
                grouped_conditions[condition].sort(key=lambda r: r['percentage'] or 0, reverse=True)
                new_rewards.extend(grouped_conditions[condition])
                del grouped_conditions[condition]

            for condition, entries in grouped_conditions.items():
                print(f"ERROR: condition {condition} should not exist")
                new_rewards.extend(entries)

            rewards_per_rank[idx] = new_rewards

        monster_entry['rewards'] = sum(rewards_per_rank, [])

    # Now save the output. The actual monsters will be reordered by this operation
    writer.save_data_csv(
        "monsters/monster_rewards.csv",
        data.monster_map,
        key="rewards",
        schema=schema.MonsterReward())
    print("Repair complete")

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
