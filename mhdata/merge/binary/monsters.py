from operator import itemgetter
from os.path import dirname, abspath, join

from mhdata.io.csv import read_csv
from .load.bcore import load_text

from mhdata.io import create_writer, DataMap
from mhdata.load import schema

def update_monsters(mhdata):
    monster_keys = read_csv(dirname(abspath(__file__)) + '/monster_map.csv')
    monster_keys = dict((r['name_en'], r) for r in monster_keys)

    monster_name_text = load_text('common/text/em_names')
    monster_info_text = load_text('common/text/em_info')
    for monster_entry in mhdata.monster_map.values():
        name_en = monster_entry.name('en')
        if name_en not in monster_keys:
            print(f'Warning: {name_en} not mapped, skipping')

        monster_key_entry = monster_keys[monster_entry.name('en')]
        key = monster_key_entry['key']
        info_key = monster_key_entry['key_info_override'] or key

        monster_entry['name'] = monster_name_text[key]
        if info_key != 'NONE':
            monster_entry['description'] = monster_info_text[f'NOTE_{info_key}_DESC']

    # Write new data
    writer = create_writer()

    writer.save_base_map_csv(
        "monsters/monster_base.csv",
        mhdata.monster_map,
        schema=schema.MonsterBaseSchema(),
        translation_filename="monsters/monster_base_translations.csv",
        translation_extra=['description']
    )

    print("Monsters updated\n")