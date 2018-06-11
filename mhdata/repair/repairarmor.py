from mhdata.io import DataMap, DataReaderWriter
from mhdata.io.csv import save_csv
from mhdata.load import load_data, cfg, schema

def repair_armor_order(writer: DataReaderWriter):
    data = load_data()

    armor_map = data.armor_map
    armorset_map = data.armorset_map

    new_armor_map = DataMap()

    # Copy all items in armorset order
    for set_entry in armorset_map.values():
        # All armor pieces in the set
        armor_names = [set_entry[part] for part in cfg.armor_parts]
        armor_names = list(filter(None, armor_names))

        armor_lang = set_entry['armor_lang']
        for armor_name in armor_names:
            armor_id = armor_map.id_of(armor_lang, armor_name)
            armor = armor_map.pop(armor_id)
            new_armor_map.insert(armor)

    # Copy over remaining items
    for remaining_item in armor_map:
        new_armor_map.insert(remaining_item)

    # Save results (todo: refactor, move to writer)
    armor_schema = schema.ArmorBaseSchema()
    result_list = new_armor_map.to_list()
    data, errors = armor_schema.dump(result_list, many=True)
    writer.save_csv("armors/armor_base.csv", data)
