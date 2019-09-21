from .load import load_quests
from .artifacts import write_dicts_artifact

def update_quests(mhdata, item_updater):
    quests = load_quests()

    # Internal helper to add a prefix to "unk" fields
    def prefix_unk_fields(basename, d):
        result = {}
        for key, value in d.items():
            if key.startswith('unk'):
                key = basename + '_' + key
            result[key] = value
        return result

    quest_artifact_entries = []
    quest_reward_artifact_entries = []
    test = set()
    for quest in quests:
        header_fields = prefix_unk_fields('header', quest.header.as_dict())
        objective_fields = prefix_unk_fields('objective', quest.objective.as_dict())

        if quest.name['en'] in test:
            print(quest.name['en'] + " is a dupe")
        test.add(quest.name['en'])

        quest_artifact_entries.append({
            'name_en': quest.name['en'],
            **header_fields,
            **objective_fields
        })

        for idx, rem in enumerate(quest.reward_data_list):
            first = True
            for (item_id, qty, chance) in rem.iter_items():
                item_name, _ = item_updater.name_and_description_for(item_id)
                if first and not rem.drop_mechanic:
                    quest_reward_artifact_entries.append({
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
    write_dicts_artifact('quest_raw_rewards.csv', quest_reward_artifact_entries)