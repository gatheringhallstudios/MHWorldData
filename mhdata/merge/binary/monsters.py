from operator import itemgetter
from os.path import dirname, abspath, join
from pathlib import Path

from mhdata.io.csv import read_csv
from mhdata.io import create_writer, DataMap
from mhdata.load import schema

from .load.bcore import load_text, get_chunk_root
from .parsers import load_epg, struct_to_json
from . import artifacts

def update_monsters(mhdata):
    root = Path(get_chunk_root())
    this_dir = dirname(abspath(__file__))

    # Attempt to load the various types of mappings that monsters have
    # Monsters have an internal numerical id used in some schemas, and varying string ids
    # used in other schemas. Note that string keysare inconsistent, so some magic is usually involved.
    # Therefore we load:
    # - Map keyed by name_en that gives the string keys for names and for hunter notes (can differ)
    # - Map keyed by internal id that connects to name_en (used for hitzones/statuses/etc)
    # - a resolved itlot filename for carve rewards
    monster_keys = read_csv(this_dir + '/monster_map.csv')
    monster_keys = dict((r['name_en'], r) for r in monster_keys)
    for key, value in monster_keys.items():
        # itlots use the hunting notes one primarily
        key_overwritten = (value['key_info_override'] or value['key'])
        value['key_overwritten'] = key_overwritten
        value['itlot_fname'] = key_overwritten + '.itlot'

        base, _, suffix = key_overwritten.partition('_')
        value['base_key'] = base
        value['subitem'] = suffix or '00'

    monster_id_entries = read_csv(this_dir + '/MonsterList.txt', fieldnames=['name', 'id'])
    monster_id_map = { int(v['id'], 16):v['name'] for v in monster_id_entries}

    # Mapping of the home folder of each monster by name
    # Currently these names are not the name_en entries, but the MonsterList entry names
    folder_for_monster = {}

    # Load hitzone entries
    hitzone_json = []
    for filename in root.joinpath('em/').rglob('*.dtt_epg'):
        epg_binary = load_epg(filename)
        json_data = struct_to_json(epg_binary)

        # Monsters are all in the same folder, so store a record of the folder for this monster
        name = monster_id_map.get(epg_binary.ingameID)
        folder_for_monster[name] = filename.parent

        hitzone_json.append({
            'name': name,
            'filename': str(filename.relative_to(root)),
            **json_data
        })

    monster_name_text = load_text('common/text/em_names')
    monster_info_text = load_text('common/text/em_info')
    for monster_entry in mhdata.monster_map.values():
        name_en = monster_entry.name('en')
        if name_en not in monster_keys:
            print(f'Warning: {name_en} not mapped, skipping')
            continue

        monster_key_entry = monster_keys[monster_entry.name('en')]
        key = monster_key_entry['key']
        info_key = monster_key_entry['key_overwritten']

        monster_entry['name'] = monster_name_text[key]
        if info_key != 'NONE':
            monster_entry['description'] = monster_info_text[f'NOTE_{info_key}_DESC']

        # Get the base folder for monster data
        base_key = monster_key_entry['base_key']
        subitem = monster_key_entry['subitem']
        monster_folder = root.joinpath(f'em/{base_key}/{subitem}/data')

        # Read hitzone data
        #epg_binary = load_epg(monster_folder.joinpath(f'{base_key}.dtt_epg'))
        #hitzone_json.append(struct_to_json(epg_binary))

    # Write hitzone data to artifacts
    artifacts.write_json_artifact("monster_hitzones.json", hitzone_json)
    print("Monster hitzones artifact written (Automerging not supported)")

    # Read drop rates
    # for filename in Path(get_chunk_root()).joinpath().rglob("*.itlot"):
    #     print(filename)

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