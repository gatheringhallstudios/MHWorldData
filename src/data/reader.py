import os
import json
import re
import collections.abc
import typing

from .datamap import DataMap
from src.util import ensure, ensure_warn

def _joindicts(*dictlist):
    "Joins multiple dictionaries without overwrite"
    result = {}
    for d in dictlist:
        for key, value in d.items():
            if key not in result:
                result[key] = value
    return result

class DataReader:

    def __init__(self, *, languages : typing.List, data_path : str):
        self.languages = languages
        self.data_path = data_path

    def get_data_path(self, *rel_path):
        """Returns a file path to a file stored in the data folder using one or more
        path components. Used internally
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(self.data_path, *rel_path)
        return os.path.normpath(data_dir)

    def load_base_map(self, data_file, validate=True):
        "Loads a base data map object."
        data_file = self.get_data_path(data_file)
        languages_with_errors = set()

        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)

        result = DataMap()    
        id = 1
        for row in data:
            entry = result.add_entry(id, row)

            # Validation prepass. Find missing langauges in the new entry
            for lang in self.languages:
                if lang not in entry['name']:
                    languages_with_errors.add(lang)
                    
            id += 1

        # If we are missing translations, do a warning or validation
        ensure_fn = ensure if validate else ensure_warn
        ensure_fn(not languages_with_errors, 
            "Missing language entries for " +
            ', '.join(languages_with_errors) +
            f" While loading {data_file}")
        
        return result    

    def load_data_map(self, parent_map : DataMap, data_file, lang="en", validate=True):
        """Loads a data file, using a base map to anchor it to id
        The result is a DataMap object mapping id -> data row
        """
        data_file = self.get_data_path(data_file)

        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)

        # Check if the data is of the correct type (is a dict)
        if not hasattr(data, 'keys'):
            raise Exception("Invalid data, the data map must be a dictionary")

        # Hold all keys yet to be joined. If any exist, it failed to to join
        datakeys = set(data.keys())

        result = {}

        for id, entry in parent_map.items():
            name = entry.name(lang)
            if name not in data:
                continue
            result[id] = _joindicts(entry, data[name])

            # Mark as success by removing from the "yet to be joined" list
            datakeys.remove(name)

        # Validation, show warning or error if some keys didn't join
        ensure_fn = ensure if validate else ensure_warn
        ensure_fn(not datakeys, 
            "Several invalid names found. Entries are " +
            ','.join(datakeys))

        return DataMap(result)

    def load_split_data_map(self, parent_map : DataMap, data_directory, lang="en", validate=True):
        """Loads a data map by combining separate maps in a folder into one.
        Just like a normal data map, it is anchored to the translation map.
        """
        data_directory = self.get_data_path(data_directory)
        
        all_subdata = []
        for dir_entry in os.scandir(data_directory):
            if not dir_entry.is_file():
                continue
            if not dir_entry.name.lower().endswith('.json'):
                continue

            with open(dir_entry, encoding="utf-8") as f:
                subdata_json = json.load(f)
            
                # Check if the data is of the correct type (is a dict)
                if not hasattr(subdata_json, 'keys'):
                    raise Exception(f"Invalid data in {dir_entry}, the data map must be a dictionary")
                
                all_subdata.append(subdata_json)

        # todo: validate key conflicts
        # todo: store origins of keys somehow
        data = _joindicts(*all_subdata)

        # Hold all keys yet to be joined. If any exist, it didn't join
        datakeys = set(data.keys())

        result = {}

        for id, entry in parent_map.items():
            name = entry.name(lang)
            if name not in data:
                continue
            result[id] = _joindicts(entry, data[name])
            datakeys.remove(name)

        # Validation, show warning or error if some keys didn't join
        ensure_fn = ensure if validate else ensure_warn
        ensure_fn(not datakeys, 
            "Several invalid names found. Invalid entries are " +
            ','.join(datakeys))

        return DataMap(result)
