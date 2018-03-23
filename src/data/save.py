import json
import collections
import os
import os.path
from .config import get_languages, get_data_path

def save_translate_map(location, translate_map):
    "Writes a translate map to a location in the data directory"
    location = get_data_path(location)
    result = []
    for row in translate_map:
        entry = {}
        for lang in get_languages():
            entry['name_'+lang] = row.get(lang, "")
        result.append(entry)

    with open(location, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def save_data_map(location, data_map):
    "Write a DataMap to a location in the data directory in translatemap order"
    location = get_data_path(location)
    items = [dict(v) for v in data_map.values()]
    with open(location, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=4, ensure_ascii=False)

def save_split_data_map(location, data_map, key_field):
    "Writes a DataMap to a folder as separated json files. The split occurs on the value of key_field"
    location = get_data_path(location)

    # Split items into buckets separated by the key field
    split_data = collections.OrderedDict()
    for item in data_map.values():
        key = item[key_field]
        split_data[key] = split_data.get(key, [])
        split_data[key].append(dict(item))

    os.makedirs(location, exist_ok=True)
    # todo: should we delete what's inside?
        
    # Write out the buckets into separate json files
    for key, items in split_data.items():
        file_location = os.path.join(location, f"{key}.json")
        if not os.path.commonprefix([location, file_location]):
            raise Exception(f"Invalid Key Location {file_location}")

        with open(file_location, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=4, ensure_ascii=False)
    