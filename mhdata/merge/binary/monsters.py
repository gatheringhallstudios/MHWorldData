from operator import itemgetter
from pathlib import Path
import itertools

from mhdata.io import create_writer, DataMap
from mhdata.load import schema

from mhdata.binary import MonsterCollection, MonsterData, ItemCollection
from mhdata.binary.load import get_chunk_root
from mhdata.binary.parsers import struct_to_json, load_itlot, load_eda
from .items import ItemUpdater
from . import artifacts

# todo: Handle Quest rewards and investigation droprates somewhere
itlot_conditions  = [
    'Track', 'Body Carve', 'Carve / Capture', 'Tail Carve', 
    'Shiny Drop', 'Palico Bonus', 'Plunderblade']
skipped_conditions = ['Investigation (Silver)', 'Investigation (Gold)', 'Quest Reward (Bronze)']

hitzone_fields = ['cut','impact','shot','fire','water','thunder','ice','dragon','ko']

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


def update_monsters(mhdata, item_data: ItemCollection, monster_data: MonsterCollection):
    root = Path(get_chunk_root())

    # Load hitzone entries. EPG files contain hitzones, parts, and base hp
    print('Loading monster hitzone data')
    if monster_data.load_epg_eda():
        print('Loaded Monster epg data (hitzones and breaks)')

    # Load status entries
    monster_statuses = read_status(monster_data)
    print('Loaded Monster status data')
    
    # Write hitzone data to artifacts
    hitzone_raw_data = [{'name': m.name['en'], **struct_to_json(m.epg)} for m in monster_data.monsters if m.epg is not None]
    artifacts.write_json_artifact("monster_hitzones_and_breaks.json", hitzone_raw_data)
    print("Monster hitzones+breaks raw data artifact written (Automerging not supported)")

    write_hitzone_artifacts(monster_data)
    print("Monster hitzones artifact written (Automerging not supported)")
    
    artifacts.write_json_artifact("monster_status.json", list(monster_statuses.values()))
    print("Monster status artifact written (Automerging not supported)")

    monster_drops = read_drops(monster_data, item_data)
    print('Loaded Monster drop rates')

    for monster_entry in mhdata.monster_map.values():
        name_en = monster_entry.name('en')
        try:
            monster = monster_data.by_name(name_en)
        except KeyError:
            print(f'Warning: Monster {name_en} not in metadata, skipping')
            continue

        monster_entry['name'] = monster.name
        if monster.description:
            monster_entry['description'] = monster.description

        # Compare drops (use the hunting notes key name if available)
        drop_tables = monster_drops.get(monster.id, None)
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

        # Compare hitzones
        hitzone_data = monster.hitzones
        if hitzone_data and 'hitzones' in monster_entry:
            # Create tuples of the values of the hitzone, to use as a comparator
            hitzone_key = lambda h: tuple(h[v] for v in hitzone_fields)

            stored_hitzones = [hitzone_key(h) for h in hitzone_data]
            stored_hitzones_set = set(stored_hitzones)

            # Check if any hitzone we have doesn't actually exist
            for hitzone in monster_entry['hitzones']:
                if hitzone_key(hitzone) not in stored_hitzones_set:
                    print(f"Validation Error: Monster {name_en} has invalid hitzone {hitzone['hitzone']['en']}")

        elif 'hitzones' not in monster_entry and hitzone_data:
            print(f'Warning: no hitzones in monster entry {name_en}, but binary data exists')
        elif 'hitzones' in monster_entry:
            print(f'Warning: hitzones exist in monster {name_en}, but no binary data exists to compare')
        else:
            print(f"Warning: No hitzone data for monster {name_en}")


        # Status info
        status = monster_statuses.get(monster.id, None)
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

def read_status(monsters: MonsterCollection):
    "Reads status data for all monsters in the form of a nested didctionary, indexed by the binary monster id"
    root = Path(get_chunk_root())

    results = {}
    for filename in root.joinpath('em/').rglob('*.dtt_eda'):
        eda_binary = load_eda(filename)
        json_data = struct_to_json(eda_binary)

        try:
            name = monsters.by_id(eda_binary.monster_id).name['en']

            results[eda_binary.monster_id] = {
                'name': name,
                'filename': str(filename.relative_to(root)),
                **json_data
            }
        except KeyError:
            pass # warn?

    return results

def read_drops(monsters: MonsterCollection, items: ItemCollection):
    """Returns a list of all monster drop tables, each indexed by the binary idea. 
    The result is a dict referring to a list of lists"""

    root = Path(get_chunk_root())

    results = {}
    for monster_entry in monsters.monsters:
        key_name = monster_entry.meta.key_name
        key_description = monster_entry.meta.key_description

        itlot_key = (key_description or key_name).lower()
        if itlot_key:
            itlot_path = root.joinpath(f"common/item/{itlot_key}.itlot")
            drops = load_itlot(itlot_path)

            monster_drops = []
            for entry in drops.entries:
                table_entries = [
                    {
                        'item_en': items.by_id(iid).name['en'],
                        'stack': qty,
                        'percentage': rarity
                    } for iid, qty, rarity, animation in entry.iter_items() if iid != 0]
                table_entries.sort(key=itemgetter('percentage'), reverse=True)
                monster_drops.append(table_entries)
                
            results[monster_entry.id] = monster_drops

    return results

def write_hitzone_artifacts(monsters: MonsterCollection):
    hitzone_raw_data_flat = []
    for monster in monsters.monsters:
        for part in monster.parts:
            for subpart in part.subparts:
                base_params = {
                    'name_en': monster.name['en'],
                    'part_id': part.id,
                    'part_name': part.name,
                    'flinch': part.flinch,
                    'cleave_type': "/".join(c[0] for c in part.cleaves),
                    'cleave_val': "/".join(str(c[1]) for c in part.cleaves),
                    'extract': part.extract,
                    'subpart': subpart.id
                }

                def add_hzv(type, hzv):
                    hitzone_raw_data_flat.append({
                        **base_params,
                        'type': type,
                        **hzv
                    })

                if subpart.hzv_base: add_hzv('base', subpart.hzv_base)
                if subpart.hzv_broken: add_hzv('broken', subpart.hzv_broken)

                if monster.name['en'] not in ['Behemoth']:
                    for idx, hzv in enumerate(subpart.hzv_special):
                        add_hzv(f'special {idx}', hzv)

        for idx in monster.unlinked_hitzones:
            hitzone_raw_data_flat.append({
                'name_en': monster.name['en'],
                'part_id': 'unlinked',
                'part_name': 'unlinked',
                'type': 'unlinked',
                **monster.hitzones[idx]
            })

    artifacts.write_dicts_artifact('monster_hitzones_raw.csv', hitzone_raw_data_flat)

def compare_dict_lists(list1, list2, fields):
    if len(list1) != len(list2):
        return False

    create_tuple = lambda i: tuple(i[k] for k in fields)

    others = set(create_tuple(i) for i in list2)

    for item in list1:
        entry = create_tuple(item)
        try:
            others.remove(entry)
        except KeyError:
            return False

    return True


def compare_drop_tables(list1, list2):
    return compare_dict_lists(list1, list2, ('item_en', 'stack', 'percentage'))
