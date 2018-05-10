import os
import re
import collections.abc
import typing
import json
import csv

from .datamap import DataMap
from .stitcher import DataStitcher
from .functions import validate_key_join
from mhwdata.util import ensure, ensure_warn, joindicts

def group_fields(obj, groups=[]):
    "Returns a new dictionary where the items that start with groupname_ are consolidated"
    result = {}
    for key, value in obj.items():
        group_results = list(filter(lambda g: key.startswith(g+'_'), groups))
        if not group_results:
            result[key] = value
            continue

        group_name = group_results[0]
        subkey = key[len(group_name)+1:]
        
        group = result.setdefault(group_name, {})
        group[subkey] = value

    return result


class DataReader:
    """A class used to deserialize objects from the data files.
    The languages parameters sets the expected languages,
    and the required languages sets the ones that are validated for existance.
    """

    def __init__(self, *,
            languages: typing.List,
            required_languages=['en'],
            data_path: str):
        self.languages = languages
        self.required_languages = required_languages
        self.data_path = data_path

        if not self.languages:
            self.languages = self.required_languages

    def get_data_path(self, *rel_path):
        """Returns a file path to a file stored in the data folder using one or more
        path components. Used internally
        """
        data_dir = os.path.join(self.data_path, *rel_path)
        return os.path.normpath(data_dir)

    def start_load(self, base_map: DataMap):
        return DataStitcher(self, base_map)

    def _validate_base_map(self, fname, basemap: DataMap, error=True):
        languages_with_errors = set()
        for entry in basemap.values():
            # Validation prepass. Find missing languages in the new entry
            for lang in self.required_languages:
                if not entry['name'].get(lang, None):
                    languages_with_errors.add(lang)

        ensure_fn = ensure if error else ensure_warn
        ensure_fn(not languages_with_errors,
            "Missing language entries for " +
            ', '.join(languages_with_errors) +
            f" While loading {fname}")

        
    def load_base_json(self, data_file, validate=True):
        "Loads a base data map object."
        data_file = self.get_data_path(data_file)

        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)

        result = DataMap()
        for row in data:
            result.insert(row)

        self._validate_base_map(data_file, result, error=validate)

        return result

    def load_base_csv(self, data_file, groups=['name'], validate=True):
        data_file = self.get_data_path(data_file)
        if 'name' not in groups:
            raise Exception("Name is a required group for base maps")
        
        result = DataMap()
        with open(data_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # grouping logic should be moved elsewhere once we get to data maps
            for row in reader:
                row = group_fields(row, groups)
                result.insert(row)

        self._validate_base_map(data_file, result, error=validate)

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
            result[id] = joindicts({}, entry, data[name])

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
        data = joindicts({}, *all_subdata)

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
            result[id] = joindicts({}, entry, data[name])

        return DataMap(result)
