from operator import itemgetter
from pathlib import Path

from mhdata.io import create_writer, DataMap
from mhdata.load import schema

from .load import load_text, get_chunk_root, MonsterMetadata
from .parsers import load_epg, struct_to_json, load_itlot
from .items import ItemUpdater
from . import artifacts


def update_monsters(mhdata, item_updater: ItemUpdater, monster_meta: MonsterMetadata):
    root = Path(get_chunk_root())

    # Mapping of the home folder of each monster by name
    # Currently these names are not the name_en entries, but the MonsterList entry names
    folder_for_monster = {}

    # Load hitzone entries
    hitzone_json = []
    for filename in root.joinpath('em/').rglob('*.dtt_epg'):
        epg_binary = load_epg(filename)
        json_data = struct_to_json(epg_binary)

        try:
            name = monster_meta.by_id(epg_binary.monster_id).name

            hitzone_json.append({
                'name': name,
                'filename': str(filename.relative_to(root)),
                **json_data
            })
        except KeyError:
            pass # warn?

    monster_name_text = load_text('common/text/em_names')
    monster_info_text = load_text('common/text/em_info')
    for monster_entry in mhdata.monster_map.values():
        name_en = monster_entry.name('en')
        if not monster_meta.has_monster(name_en):
            print(f'Warning: Monster {name_en} not in metadata, skipping')
            continue

        monster_key_entry = monster_meta.by_name(name_en)
        key_name = monster_key_entry.key_name
        key_description = monster_key_entry.key_description

        monster_entry['name'] = monster_name_text[key_name]
        if key_description:
            monster_entry['description'] = monster_info_text[f'NOTE_{key_description}_DESC']

        # Read drops (use the hunting notes key name if available)
        itlot_key = (key_description or key_name).lower()
        if itlot_key:
            itlot_path = root.joinpath(f"common/item/{itlot_key}.itlot")
            drops = load_itlot(itlot_path)

            monster_drops = []
            for idx, entry in enumerate(drops.entries):
                monster_drops.extend(
                    [{
                        'group': f'Group {idx+1}',
                        'item_name': item_updater.name_for(iid)['en'],
                        'quantity': qty,
                        'percentage': rarity
                    } for iid, qty, rarity, animation in entry.iter_items() if iid != 0]
                )
            artifacts.write_dicts_artifact(f'monster_drops/{name_en} drops.csv', monster_drops)
        else:
            print(f'Warning: no drops file found for monster {name_en}')

    # Write hitzone data to artifacts
    artifacts.write_json_artifact("monster_hitzones.json", hitzone_json)
    print("Monster hitzones artifact written (Automerging not supported)")

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