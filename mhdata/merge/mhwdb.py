import requests
from mhdata.io import create_writer
from mhdata.load import load_data, schema

writer = create_writer()

# note: inc means incoming

def merge_weapons():
    inc_data = requests.get("https://mhw-db.com/weapons").json()
    data = load_data().weapon_map

    not_exist = []
    mismatches_atk = []
    mismatches_def = []
    mismatches_other = []

    def print_all(items):
        for item in items:
            print(item)
        print()

    for weapon_inc in inc_data:
        inc_id = weapon_inc['id']
        inc_type = weapon_inc['type']
        name = weapon_inc['name']
        inc_label = f"{name} ({inc_type})"

        # Our system uses I/II/III, their's uses 1/2/3
        if name not in data.names('en'):
            name = name.replace(" 3", " III")
            name = name.replace(" 2", " II")
            name = name.replace(" 1", " I")

        if name not in data.names('en'):
            not_exist.append(f"{name} does not exist ({inc_type} {inc_id}).")
            continue # todo: add to our database

        existing = data.entry_of('en', name)
        
        # Incoming basic data for the weapon entry
        inc_attack = weapon_inc['attack']['display']
        inc_defense = weapon_inc['attributes'].get('defense', 0)
        inc_phial = weapon_inc['attributes'].get('phialType', None)
        inc_phial_power = None
        inc_kinsect = weapon_inc['attributes'].get('boostType', None)
        inc_affinity = weapon_inc['attributes'].get('affinity', 0)

        # Ensure minimum of 3 slots (avoid out of bounds)
        weapon_inc['slots'] += [{'rank':0}] * 3
        inc_slot1 = weapon_inc['slots'][0]['rank']
        inc_slot2 = weapon_inc['slots'][1]['rank']
        inc_slot3 = weapon_inc['slots'][2]['rank']

        # If there are two values and the second is a number, populate the phial power
        if inc_phial and ' ' in inc_phial:
            values = inc_phial.split(' ')
            if len(values) == 2 and values[1].isdigit():
                inc_phial = values[0]
                inc_phial_power = int(values[1])

        inc_shelling_type = None
        inc_shelling_level = None
        if 'shellingType' in weapon_inc['attributes']:
            (left, right) = weapon_inc['attributes']['shellingType'].split(' ')
            inc_shelling_type = left.lower()
            inc_shelling_level = int(right.lower().replace('lv', ''))

        # Simple validation comparisons
        if existing['attack'] != inc_attack:
            mismatches_atk.append(f"WARNING: {inc_label} has mismatching attack " +
                f"(internal {existing['attack']} | external {inc_attack} | ext id {inc_id})")
        if (existing['defense'] or 0) != inc_defense:
            mismatches_def.append(f"WARNING: {inc_label} has mismatching defense " +
                f"(internal {existing['defense']} | external {inc_defense} | ext id {inc_id})")
        if existing['kinsect_bonus'] and existing['kinsect_bonus'] != inc_kinsect:
            mismatches_other.append(f"Warning: {inc_label} has mismatching kinsect bonus")
        if existing['phial'] and existing['phial'] != inc_phial:
            mismatches_other.append(f"WARNING: {inc_label} has mismatching phial")
        if existing['phial_power'] and existing['phial_power'] != inc_phial_power:
            mismatches_other.append(f"WARNING: {inc_label} has mismatching phial power")
        if existing['shelling'] and existing['shelling'] != inc_shelling_type:
            mismatches_other.append(f"Warning: {inc_label} has mismatching shell type")
        if existing['shelling_level'] and existing['shelling_level'] != inc_shelling_level:
            mismatches_other.append(f"Warning: {inc_label} has mismatching shell level")

        def copy_maybe(field_name, value):
            "Inner function to copy a value if no value exists and there is a new val"
            if not existing[field_name] and value:
                existing[field_name] = value

        def copy_with_warning(field_name, value):
            if existing[field_name] != value:
                print(f"OVERRIDING: {inc_label} will get new {field_name}")
                existing[field_name] = value

        # Copy over new base data if there are new fields
        copy_maybe('kinsect_bonus', inc_kinsect)
        copy_maybe('phial', inc_phial)
        copy_maybe('phial_power', inc_phial_power)
        copy_maybe('shelling', inc_shelling_type)
        copy_maybe('shelling_level', inc_shelling_level)
        copy_maybe('affinity', inc_affinity)

        # Copy over with warning. TODO: Add arg to require opt in to overwrite slots
        copy_with_warning('slot_1', inc_slot1)
        copy_with_warning('slot_2', inc_slot2)
        copy_with_warning('slot_3', inc_slot3)

        # Add sharpness data for anything that's missing sharpness data
        if 'durability' in weapon_inc and not existing.get('sharpness', None):
            inc_sharpness = weapon_inc['durability'][5]
            maxed = weapon_inc['durability'][0] == inc_sharpness
            existing['sharpness'] = {
                'maxed': 'TRUE' if maxed else 'FALSE',
                'red': inc_sharpness['red'],
                'orange': inc_sharpness['orange'],
                'yellow': inc_sharpness['yellow'],
                'green': inc_sharpness['green'],
                'blue': inc_sharpness['blue'],
                'white': inc_sharpness['white'],
                'purple': 0
            }
        

    # print errors and warnings
    print_all(not_exist)
    print_all(mismatches_atk)
    print_all(mismatches_def)
    print_all(mismatches_other)

    weapon_base_schema = schema.WeaponBaseSchema()
    writer.save_base_map_csv('weapons/weapon_base_NEW.csv', data, schema=weapon_base_schema)
    writer.save_data_csv('weapons/weapon_sharpness_NEW.csv', data, key='sharpness')
