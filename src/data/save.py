# The save methods are not part of the build process
# They are used whenever I am pulling new data from other sources.

import json
import collections
import os
import os.path

from .config import get_languages, get_data_path
from .datamap import DataMap

def save_base_map(location, base_map):
    "Writes a data map to a location in the data directory"
    location = get_data_path(location)
    result = []
    for row in base_map.values():
        entry = dict(row)
        result.append(entry)

    with open(location, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def save_data_map(location, base_map, data_map, lang='en'):
    """Write a DataMap to a location in the data directory in in the base map's order.
    Data that already exists in the provided base map (like name data) are not written out
    """
    location = get_data_path(location)
    result = {}
    for entry in data_map.values():
        base_entry = base_map[entry.id]
        
        # Create the result entry. Fields are copied EXCEPT for base ones
        result_entry = {}
        for key, value in entry.items():
            if key not in base_entry:
                result_entry[key] = value

        # Add to result
        result[entry.name(lang)] = result_entry
        
    with open(location, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def save_split_data_map(location, base_map, data_map, key_field, lang='en'):
    """Writes a DataMap to a folder as separated json files. 
    The split occurs on the value of key_field.
    Fields that exist in the base map are not copied to the data maps
    """
    location = get_data_path(location)

    # Split items into buckets separated by the key field
    split_data = collections.OrderedDict()
    for entry in data_map.values():
        base_entry = base_map[entry.id]
        
        # Create the result entry. Fields are copied EXCEPT for base ones
        result_entry = {}
        for key, value in entry.items():
            if key not in base_entry:
                result_entry[key] = value

        # Add to result, key'd by the key field
        split_key = entry[key_field]
        split_data[split_key] = split_data.get(split_key, {})
        split_data[split_key][entry.name(lang)] = result_entry

    os.makedirs(location, exist_ok=True)
    # todo: should we delete what's inside?
        
    # Write out the buckets into separate json files
    for key, items in split_data.items():
        file_location = os.path.join(location, f"{key}.json")

        # Validation to make sure there's no backpathing
        if not os.path.commonprefix([location, file_location]):
            raise Exception(f"Invalid Key Location {file_location}")

        with open(file_location, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=4, ensure_ascii=False)
    