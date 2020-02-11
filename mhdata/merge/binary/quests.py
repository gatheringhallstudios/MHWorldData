import collections
from string import ascii_uppercase

from mhdata import cfg, typecheck
from mhdata.io import create_writer, DataMap
from mhdata.util import flatten_dict
from mhdata.load import schema

from mhdata.binary.metadata import MonsterMetadata
from mhdata.binary.load import load_quests
from mhdata.binary.parsers import struct_to_json

from .artifacts import write_dicts_artifact
from .items import ItemUpdater

def update_quests(mhdata, item_updater: ItemUpdater, monster_meta: MonsterMetadata, area_map):
    print('Beginning load of quest binary data')
    quests = load_quests()
    print('Loaded quest binary data')
    
    quest_data = [get_quest_data(q, item_updater, monster_meta, area_map) for q in quests]

    quest_by_id = { q.id:q for q in quests }
    quest_data_by_id = { q['id']:q for q in quest_data }

    # test for duplicates first. 
    duplicate_candidates = get_quests_with_duplicate_names(quest_by_id)
    for (q1, q2) in duplicate_candidates:
        quest2_data = quest_data_by_id[q2.id]
        if compare_quest_data(quest_data_by_id[q1.id], quest2_data):
            quest_name = q1.name['en']
            print(f'Warning: Quest {quest_name} has exact duplicates.')

    write_quest_raw_data(quests, item_updater, monster_meta)
    print('Quest artifacts written. Copy ids and names to quest_base.csv to add to build')

    # Merge the quest data
    for raw in quest_data:
        existing_entry = mhdata.quest_map.get(raw['id'])
        if existing_entry:
            existing_entry.update(raw)
    print('Quests merged')

    writer = create_writer()

    writer.save_base_map_csv(
        "quests/quest_base.csv",
        mhdata.quest_map,
        translation_filename="quests/quest_base_translations.csv",
        translation_extra=['objective', 'description'],
        schema=schema.QuestBaseSchema(),
        key_join='id'
    )

    writer.save_data_csv(
        'quests/quest_monsters.csv',
        mhdata.quest_map,
        key='monsters',
        key_join='id'
    )

    writer.save_data_csv(
        'quests/quest_rewards.csv',
        mhdata.quest_map,
        key='rewards',
        key_join='id'
    )

    print('Quest files updated\n')

def get_quest_data(quest, item_updater: ItemUpdater, monster_meta: MonsterMetadata, area_map):
    "Returns a dictionary of resolved quest data, marking items used in the item updater"

    binary = quest.binary

    result = {
        'id': quest.id,
        'name': quest.name,
        'objective': quest.objective,
        'description': quest.description,
        'stars': binary.header.starRating,
        'location_en': area_map[binary.header.mapId],
        'quest_type': None,
        'zenny': binary.header.zennyReward,
        'monsters': [],
        'rewards': []
    }

    monster_entries = {}

    def get_monster(monster_id):
        monster_name = monster_meta.by_id(monster_id).name
        return monster_entries.get(monster_name)

    def add_monster(monster_id, quantity, objective=False):
        monster_name = monster_meta.by_id(monster_id).name
        existing_entry = get_monster(monster_id)
        if existing_entry:
            existing_entry['quantity'] += quantity
        else:
            entry = {
                'monster_en': monster_name,
                'quantity': quantity,
                'is_objective': objective
            }
            result['monsters'].append(entry)
            monster_entries[monster_name] = entry

    # Note about quest type:
    # The values are powers of 2, so it could be a bitwise flag system,
    # however only one bit is ever set at a time. Check again after Iceborne
    # 1 - Hunt
    # 2 - small monsters
    # 4 - capture
    # 8 - delivery (no monsters are objectives)
    # 16 - hunt N monsters
    # 32 - probably special story

    # Note about objective types:
    # 0 - seems to be when there is no data
    # 1 (with event 4) - Hunt N monsters
    # 2 - item turn in
    # 17 - capture
    # 33 - small monster
    # 49 - large monster

    # Using objective type the logic becomes simpler (flag as we go) however we can fall back to quest type if we must

    quest_type = binary.objective.quest_type
    objectives = binary.objective.objectives

    # if subobjectives have a value, use the sub objective instead of the main objectives
    # This only happens in Kestodon Kerfluffle. The logic may have to change for Iceborne.
    if binary.objective.sub_objectives[0].objective_id != 0:
        objectives = binary.objective.sub_objectives
    
    # Go through objectives, setting the quest type and adding monsters
    for obj in objectives:
        if obj.objective_type == 0:
            continue

        # Set the quest type.
        # Because of the existance of type 32, we use the objective type to figure out the quest type
        if result['quest_type'] is None:
            if (obj.objective_type == 1 and obj.event == 4) or obj.objective_type in [33, 49]:
                result['quest_type'] = 'hunt'
            elif obj.objective_type == 17:
                result['quest_type'] = 'capture'
            elif obj.objective_type == 2:
                result['quest_type'] = 'deliver'
            else:
                raise Exception(f"Unknown objective type {obj.objective_type} in quest {quest.name['en']}")
        
        if obj.objective_type in [17, 33, 49]:
            add_monster(obj.objective_id, obj.objective_amount, True)
        elif obj.objective_type == 1 and obj.event == 4:
            for i in range(obj.objective_amount):
                add_monster(binary.monsters[i].monster_id, 1, True)
        elif obj.objective_type == 2:
            pass # item turn in, not handled yet

    # Now add the remaining monsters
    for monster in binary.monsters:
        monster_id = monster.monster_id
        if monster_id == -1 or get_monster(monster_id):
            continue
        
        # Kulve Taroth is a special exception
        monster_name = monster_meta.by_id(monster_id).name
        if monster_name in ['Kulve Taroth', 'Zorah Magdaros']:
            result['quest_type'] = 'assignment'
            add_monster(monster_id, 1, True)
        else:
            add_monster(monster_id, 1)

    # quest rewards
    for idx, rem in enumerate(quest.reward_data_list):
        group = ascii_uppercase[idx]

        first = True
        for (item_id, qty, chance) in rem.iter_items():

            item_name, _ = item_updater.name_and_description_for(item_id)
            if first and not rem.drop_mechanic:
                result['rewards'].append({
                    'group': group,
                    'item_en': item_name['en'],
                    'stack': qty,
                    'percentage': 100
                })

            first = False

            result['rewards'].append({
                'group': group,
                'item_en': item_name['en'],
                'stack': qty,
                'percentage': chance
            })

    # more special exceptions
    if quest.name['en'] in ['The Legendary Beast']:
        result['quest_type'] = 'hunt'

    return result

def compare_quest_data(quest_data1, quest_data2):
    "Compares the data in both quest datas recursively. Skips certain fields such as id"

    ignored_fields = ['id', 'description']

    if type(quest_data1) != type(quest_data2):
        return False
    if isinstance(quest_data1, collections.Mapping):
        if len(quest_data1) != len(quest_data2):
            return False
        for key, value in quest_data1.items():
            if key in ignored_fields:
                continue

            if key not in quest_data2:
                return False
            if isinstance(value, collections.Mapping):
                if not compare_quest_data(value, quest_data2[key]):
                    return False
            elif value != quest_data2[key]:
                return False

        return True

    return quest_data1 == quest_data2

def get_duplicates_for_lang(quests, lang):
    "Get all quests with duplicate names in a particular language"
    test = set()

    results = set()
    name_to_quest = {}
    for quest in quests:
        quest_key = (quest.name[lang], quest.binary.header.starRating)
        if quest_key in test:
            results.add((name_to_quest[quest_key].id, quest.id))
        else:
            test.add(quest_key)
            name_to_quest[quest_key] = quest

    return results

def get_quests_with_duplicate_names(quest_by_id):
    all_dupes = set()
    for lang in cfg.supported_languages:
        all_dupes.update(get_duplicates_for_lang(quest_by_id.values(), lang))

    results = []

    for (q1_id, q2_id) in all_dupes:
        langs_that_match = []
        quest1 = quest_by_id[q1_id]
        quest2 = quest_by_id[q2_id]
        for lang in cfg.supported_languages:
            if quest1.name[lang] == quest2.name[lang]:
                langs_that_match.append(lang)

        if len(langs_that_match) == len(cfg.supported_languages):
            print(f"{quest1.name['en']} has a complete name match for all languages")
            results.append((quest1, quest2))
        else:
            # todo: report the partial matches somehow through some other means
            langs = ", ".join(langs_that_match)
            print(f"{quest1.name['en']} is a partial name match with {quest2.name['en']} in these languages: {langs}")
        
    return results

def write_quest_raw_data(quests, item_updater: ItemUpdater, monster_meta: MonsterMetadata):
    "Writes the artifact file for the quest"
    quest_artifact_entries = []
    quest_monsters_artifact_entries = []
    quest_reward_artifact_entries = []

    # Internal helper to add a prefix to "unk" fields
    def prefix_unk_fields(basename, d):
        result = {}
        for key, value in d.items():
            if key.startswith('unk'):
                key = basename + '_' + key
            result[key] = value
        return result

    def prefix_fields(prefix, d):
        return { f'{prefix}{k}':v for k, v in d.items() }

    for quest in quests:
        binary = quest.binary

        quest_artifact_entries.append({
            'id': quest.id,
            'name_en': quest.name['en'],
            **flatten_dict(struct_to_json(binary.header), 'header'),
            **flatten_dict(struct_to_json(binary.objective), 'obj')
        })

        # handle monsters
        for monster_mib in quest.binary.monsters:
            if monster_mib.monster_id == -1:
                continue

            monster_name = None
            try:
                monster_name = monster_meta.by_id(monster_mib.monster_id).name
            except KeyError:
                pass

            quest_monsters_artifact_entries.append({
                'id': quest.id,
                'name_en': quest.name['en'],
                'monster_name': monster_name,
                **monster_mib.as_dict(),
            })

        # handle rewards
        for idx, rem in enumerate(quest.reward_data_list):
            first = True
            for (item_id, qty, chance) in rem.iter_items():
                item_name, _ = item_updater.name_and_description_for(item_id)
                if first and not rem.drop_mechanic:
                    quest_reward_artifact_entries.append({
                        'id': quest.id,
                        'name_en': quest.name['en'],
                        'reward_idx': idx,
                        'signature?': rem.signature,
                        'signatureExt?': rem.signatureExt,
                        'drop_mechanic': rem.drop_mechanic,
                        'item_name': item_name['en'],
                        'qty': qty,
                        'chance': 100
                    })

                quest_reward_artifact_entries.append({
                    'name_en': quest.name['en'],
                    'reward_idx': idx,
                    'signature?': rem.signature,
                    'signatureExt?': rem.signatureExt,
                    'drop_mechanic': rem.drop_mechanic,
                    'item_name': item_name['en'],
                    'qty': qty,
                    'chance': chance
                })
                first = False

    write_dicts_artifact('quest_raw_data.csv', quest_artifact_entries)
    write_dicts_artifact('quest_raw_monsters.csv', quest_monsters_artifact_entries)
    write_dicts_artifact('quest_raw_rewards.csv', quest_reward_artifact_entries)