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

        # Copy over data if there are new fields
        if not existing['kinsect_bonus'] and inc_kinsect:
            existing['kinsect_bonus'] = inc_kinsect
        if not existing['phial'] and inc_phial:
            existing['phial'] = inc_phial
        if not existing['phial_power'] and inc_phial_power:
            existing['phial_power'] = inc_phial_power
        if not existing['shelling'] and inc_shelling_type:
            existing['shelling'] = inc_shelling_type
        if not existing['shelling_level'] and inc_shelling_level:
            existing['shelling_level'] = inc_shelling_level

    # print errors and warnings
    print_all(not_exist)
    print_all(mismatches_atk)
    print_all(mismatches_def)
    print_all(mismatches_other)

    weapon_base_schema = schema.WeaponBaseSchema()
    writer.save_base_map_csv('weapons/weapon_base_NEW.csv', data, schema=weapon_base_schema)
