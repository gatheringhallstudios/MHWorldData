import os
import json
import re
import collections.abc
import typing

from .datamap import DataMap
from src.util import ensure, ensure_warn

def merge_without_overwrite(dest, *dictlist):
    "Merges one or more dictionaries into dest, without overwriting existing entries"
    result = dest
    for d in dictlist:
        for key, value in d.items():
            if key not in result:
                result[key] = value
    return result

def _joindicts(*dictlist):
    "Joins multiple dictionaries without overwrite, returning a new one"
    result = {}
    return merge_without_overwrite(result, *dictlist)

def validate_key_join(data_map : DataMap, keys : typing.Set, *, join_lang='en'):
    """Validates if the set of keys can be joined to the data map.
    Returns a list of violations on failure"""
    data_names = data_map.names(join_lang)
    return [key for key in keys if key not in data_names]

class DataStitcher:
    def __init__(self, reader, data_map, *, join_lang='en'):
        self.reader = reader
        self.data_map = data_map
        self.join_lang = join_lang

    def add_data(self, data_file, *, key=None):
        """
        Loads a data map to add data to the base map and returns self.
        If a key is given, it will be added under key, 
        Otherwise it will be merged without overwrite.
        """

        data_file = self.reader.get_data_path(data_file)
        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)
        
        # validation, make sure it links
        unlinked = validate_key_join(self.data_map, data.keys(), join_lang=self.join_lang)
        if unlinked:
            raise Exception(
                "Several invalid names found. Invalid entries are " +
                ','.join(unlinked))


        # validation complete, it may not link to all base entries but thats ok
        for data_key, data_entry in data.items():
            base_entry = self.data_map.entry_of(self.join_lang, data_key)
            
            if key:
                base_entry[key] = data_entry
            elif hasattr(data_entry, 'keys'):
                merge_without_overwrite(base_entry, data_entry)
            else:
                # If we get here, its a key-less merge with a non-dict
                # We cannot merge a dictionary with a non-dictionary
                raise Exception("Invalid data, the data map must be a dictionary for a keyless merge")
            
        return self

    def get(self):
        return self.data_map

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

    def start_load(self, base_data_file):
        base_map = self.load_base_map(base_data_file)
        return DataStitcher(self, base_map)

    def load_base_map(self, data_file, validate=True):
        "Loads a base data map object"
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
        The result is a DataMap object mapping id -> data row.
        Entries that the data map does not contain are not added.
        """
        data_file = self.get_data_path(data_file)

        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)

        # Check if the data is of the correct type (is a dict)
        if not hasattr(data, 'keys'):
            raise Exception("Invalid data, the data map must be a dictionary")
  
        # Set validation function depending on validation setting
        ensure_fn = ensure if validate else ensure_warn

        # Look for invalid keys; warn or fail if any
        unlinked = validate_key_join(parent_map, data.keys(), join_lang=lang)
        ensure_fn(not unlinked, 
            "Several invalid names found. Invalid entries are " +
            ','.join(unlinked))

        result = {}
        for id, entry in parent_map.items():
            name = entry.name(lang)
            if name not in data:
                continue
            result[id] = _joindicts(entry, data[name]) 

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

        # Set validation function depending on validation setting
        ensure_fn = ensure if validate else ensure_warn

        # Hold all keys yet to be joined. If any exist, it didn't join
        unlinked = validate_key_join(parent_map, data.keys(), join_lang=lang)
        ensure_fn(not unlinked, 
            "Several invalid names found. Invalid entries are " +
            ','.join(unlinked))

        result = {}
        for id, entry in parent_map.items():
            name = entry.name(lang)
            if name not in data:
                continue
            result[id] = _joindicts(entry, data[name])

        return DataMap(result)
