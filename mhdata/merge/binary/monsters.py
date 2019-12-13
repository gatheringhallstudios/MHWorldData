from operator import itemgetter
from pathlib import Path
import itertools

from mhdata.io import create_writer, DataMap
from mhdata.load import schema

from .load import load_text, get_chunk_root, MonsterMetadata
from .parsers import load_epg, struct_to_json, load_itlot, load_eda
from .items import ItemUpdater
from . import artifacts

# todo: Handle Quest rewards and investigation droprates somewhere
itlot_conditions  = [
    'Track', 'Body Carve', 'Carve / Capture', 'Tail Carve', 
    'Shiny Drop', 'Palico Bonus', 'Plunderblade']
skipped_conditions = ['Investigation (Silver)', 'Investigation (Gold)', 'Quest Reward (Bronze)']

# Note - general pattern for (small) monster drop itlos
# Group 1 - LR Carves
# Group 2 - HR Carves
# Group 3 - LR Plunderblade
# Group 4 - HR Plunderblade

# Note - general pattern for (large) monster drop itlots are (sometimes broken like say, teo)
# Work in progress, edit as analyzed
# Tail carves vary. Shiny drops usually show earlier than plunderblade
# Group 1 - Low rank Carves
# Group 2 - Low rank tail carves
# Group 5 - High Rank Carves
# Group 6 - High rank tail carve (sometimes)
# Group 7 - High rank Shiny
# Group 10 - High rank tail carve (sometimes)
# Group 12 - Low rank Plunderblade
# Group 13 - High rank Plunderblade
# Group 15 - Low rank Palico Bonus (or shiny, unsure)
# Group 16 - High rank Palico Bonus (or shiny, unsure)
# Group 21 - Low rank track
# Group 22 - High rank track

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
    print('Loaded Monster hitzone data')

    # Load status entries
    monster_statuses = read_status(monster_meta)
    print('Loaded Monster status data')
    
    # Write hitzone data to artifacts
    artifacts.write_json_artifact("monster_hitzones.json", hitzone_json)
    print("Monster hitzones artifact written (Automerging not supported)")
    artifacts.write_json_artifact("monster_status.json", list(monster_statuses.values()))
    print("Monster status artifact written (Automerging not supported)")


    monster_name_text = load_text('common/text/em_names')
    monster_info_text = load_text('common/text/em_info')

    monster_drops = read_drops(monster_meta, item_updater)
    print('Loaded Monster drop rates')

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
        drop_tables = monster_drops.get(monster_key_entry.id, None)
        if drop_tables:
            # Write drops to artifact files
            joined_drops = []
            for idx, drop_table in enumerate(drop_tables):
                joined_drops.extend({'group': f'Group {idx+1}', **e} for e in drop_table)
            artifacts.write_dicts_artifact(f'monster_drops/{name_en} drops.csv', joined_drops)

            # Check if any drop table in our current database is invalid
            if 'rewards' in monster_entry:
                rewards_sorted = sorted(monster_entry['rewards'], key=itemgetter('condition_en'))
                rewards = itertools.groupby(rewards_sorted, key=lambda r: (r['condition_en'], r['rank']))

                for (condition, rank), existing_table in rewards:
                    if condition in itlot_conditions:
                        existing_table = list(existing_table)
                        if not any(compare_drop_tables(existing_table, table) for table in drop_tables):
                            print(f"Validation Error: Monster {name_en} has invalid drop table {condition} in {rank}")
        else:
            print(f'Warning: no drops file found for monster {name_en}')

        # Status info
        status = monster_statuses.get(monster_key_entry.id, None)
        if status:
            test = lambda v: v['base'] > 0 and v['decrease'] > 0
            monster_entry['pitfall_trap'] = True if test(status['pitfall_trap_buildup']) else False
            monster_entry['shock_trap'] = True if test(status['shock_trap_buildup']) else False
            monster_entry['vine_trap'] = True if test(status['vine_trap_buildup']) else False

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

def read_status(monster_meta: MonsterMetadata):
    "Reads status data for all monsters in the form of a nested didctionary, indexed by the binary monster id"
    root = Path(get_chunk_root())

    results = {}
    for filename in root.joinpath('em/').rglob('*.dtt_eda'):
        eda_binary = load_eda(filename)
        json_data = struct_to_json(eda_binary)

        try:
            name = monster_meta.by_id(eda_binary.monster_id).name

            results[eda_binary.monster_id] = {
                'name': name,
                'filename': str(filename.relative_to(root)),
                **json_data
            }
        except KeyError:
            pass # warn?

    return results

def read_drops(monster_meta: MonsterMetadata, item_updater: ItemUpdater):
    """Returns a list of all monster drop tables, each indexed by the binary idea. 
    The result is a dict referring to a list of lists"""

    root = Path(get_chunk_root())

    results = {}
    for monster_entry in monster_meta.entries():
        key_name = monster_entry.key_name
        key_description = monster_entry.key_description

        itlot_key = (key_description or key_name).lower()
        if itlot_key:
            itlot_path = root.joinpath(f"common/item/{itlot_key}.itlot")
            drops = load_itlot(itlot_path)

            monster_drops = []
            for entry in drops.entries:
                table_entries = [
                    {
                        'item_en': item_updater.name_for(iid)['en'],
                        'stack': qty,
                        'percentage': rarity
                    } for iid, qty, rarity, animation in entry.iter_items() if iid != 0]
                table_entries.sort(key=itemgetter('percentage'), reverse=True)
                monster_drops.append(table_entries)
                
            results[monster_entry.id] = monster_drops

    return results

def compare_drop_tables(drop_table1, drop_table2):
    if len(drop_table1) != len(drop_table2):
        return False

    create_tuple = lambda i: (i['item_en'], i['stack'], i['percentage'])

    others = set(create_tuple(i) for i in drop_table2)

    for item in drop_table1:
        entry = create_tuple(item)
        try:
            others.remove(entry)
        except KeyError:
            return False

    return True