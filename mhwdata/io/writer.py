# The save methods are not part of the build process
# They are used whenever I am pulling new data from other sources.

import json
import collections
import os
import os.path

from .reader import DataReader
from .datamap import DataMap

class DataReaderWriter(DataReader):
    "A data reader that can also be used to create and update data"
    
    def save_base_map(self, location, base_map):
        "Writes a data map to a location in the data directory"
        location = self.get_data_path(location)
        result = []
        for row in base_map.values():
            entry = dict(row)
            result.append(entry)

        with open(location, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    def save_data_map(self, location, data_map, *, root=None, fields=None, lang='en'):
        """Write a DataMap to a location in the data directory.

        If root is a string, then the saving is restricted to what's inside that key.
        The result is flattened such that the root field doesn't exist in the output.
        
        If root is a data map, then fields also within the base map are omitted
        
        If fields are given, only fields within the list are exported
        """
        location = self.get_data_path(location)

        result = {}

        if not root and not fields:
            raise Exception("Either a root (string or dictionary) or a list of fields " +
                "must be given when persisting a data map")

        root_is_string = isinstance(root, str)

        for entry_id, entry in data_map.items():
            name = entry.name(lang)

            # stores the result for this round
            result_entry = {}

            # If the root is a string, use the field as the entry (if it exists)
            # if the root field doesn't exist, skip to the next
            if root and root_is_string:
                if root not in entry:
                    continue
                entry = entry[root]

            if fields:
                # If fields is given, always save them regardless of location
                for field in fields:
                    if field not in entry:
                        continue
                    result_entry[field] = entry[field]
            else:
                # check the fields in the entry to copy them over
                for key, value in entry.items():
                    # if root is not a string, assume its a base map
                    # If the field is part of the base map, then skip
                    if root and not root_is_string:
                        base_entry = root[entry.id]
                        if key in base_entry:
                            continue
                    
                    result_entry[key] = value

            if result_entry:
                result[name] = result_entry

        with open(location, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    def save_split_data_map(self, location, base_map, data_map, key_field, lang='en'):
        """Writes a DataMap to a folder as separated json files. 
        The split occurs on the value of key_field.
        Fields that exist in the base map are not copied to the data maps
        """
        location = self.get_data_path(location)

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
        