import os
import re
import collections.abc
import typing
import json
import re

from mhdata.util import ensure, ensure_warn, joindicts

from .datamap import DataMap
from mhdata.util import group_fields
from .functions import unflatten

from mhdata.io.csv import read_csv

def validate_key_join(data_map : DataMap, keys : typing.Set, *, join_lang='en'): 
    """Validates if the set of keys can be joined to the data map. 
     
    Returns a list of violations on failure.
    
    TODO: Once all merging moves to the datamap.merge() function, this will be removed""" 
    data_names = data_map.names(join_lang) 
    return [key for key in keys if key not in data_names] 


class DataReader:
    """A class used to deserialize objects from the data files.
    The languages parameters sets the expected languages,
    and the required languages sets the ones that are validated for existance.
    """

    def __init__(self, *,
            languages: typing.List,
            required_languages=('en',),
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

    def load_list_csv(self, data_file, *, schema=None):
        """Loads a simple csv without processing. 
        Accepts marshmallow schema to transform and validate it"""
        data_file = self.get_data_path(data_file)
        data = read_csv(data_file)

        if schema:
            # When version 3 is released, this api will change
            # load will just return converted and errors will auto-raise
            (converted, errors) = schema.load(data, many=True)
            if errors:
                raise Exception(str(errors))
            data = converted

        return data

        
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

    def load_base_csv(self, data_file, groups=[], validate=True):
        """Loads a base data map object from a csv
        groups is a list of additional fields (name is automatically include)
        that nest via groupname_subfield.
        """
        data_file = self.get_data_path(data_file)
        groups = ['name'] + groups

        rows = read_csv(data_file)
        rows = [group_fields(row, groups=groups) for row in rows]

        basemap = DataMap()
        basemap.extend(rows)
        self._validate_base_map(data_file, basemap, error=validate)

        return basemap

    def load_data_json(self, parent_map : DataMap, data_file, *, lang="en", key=None):
        """Loads a data file, using a base map to anchor it to id
        The parent_map is updated to map id -> data row.
        Returns the parent_map to support chaining
        """
        data_file = self.get_data_path(data_file)

        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)

        parent_map.merge(data, lang=lang, key=key)
        return parent_map

    def load_data_csv(self, parent_map : DataMap, data_file, *, key=None, groups=[], leaftype):
        """Loads a data file, using a base map to anchor it to id
        The parent_map is updated to map id -> data row.
        Returns the parent_map to support chaining.

        Language is automatically determined by the name of the first column.
        """
        
        data_file = self.get_data_path(data_file)

        if leaftype == 'list' and not key:
            raise ValueError("key is required if leaftype is list")
        
        rows = read_csv(data_file)

        if not rows:
            return parent_map

        # Auto detect language
        first_column = next(iter(rows[0].keys()))
        match = re.match('name_([a-zA-Z]+)', first_column)
        if not match:
            raise Exception("First column needs to be a name_{lang} column")
        
        lang = match.group(1)
        data = unflatten(rows, nest=[first_column], groups=groups, leaftype=leaftype)

        return parent_map.merge(data, lang=lang, key=key)

    def load_split_data_map(self, parent_map : DataMap, data_directory, lang="en", validate=True):
        """Loads a data map by combining separate maps in a folder into one.
        Just like a normal data map, it is anchored to the translation map.
        """
        #TODO: WILL BE REFACTORED TO USE THE NEW MERGE-FLOW
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
