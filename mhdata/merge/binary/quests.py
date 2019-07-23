from .load import load_quests
from .artifacts import write_dicts_artifact

def update_quests(mhdata):
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

        for rem in quest.reward_data_list:
            for (item_id, qty, chance) in zip(rem.item_ids, rem.item_qtys, rem.item_chances):
                if not item_id or not qty:
                    continue
                #print(item_id, qty, chance)

    write_dicts_artifact('quest_raw_data.csv', quest_artifact_entries)