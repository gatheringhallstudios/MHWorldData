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

def apply_schema_to_map(map, schema):
    "Internal helper to apply a marshmallow schema to the values of a map."
    errors = []
    for key in map.keys():
        value = map[key]
        (converted, val_errors) = schema.load(value, many=False)
        if val_errors:
            errors.append(val_errors)
        else:
            map[key] = converted
    if errors:
        raise Exception(str(errors))
    return map

class DataReader:
    """A class used to deserialize objects from the data files.
    The languages parameters sets the expected languages,
    and the required languages sets the ones that are validated for existance.
    """

    def __init__(self, *,
            languages: typing.List,
            data_path: str):
        self.languages = languages
        self.data_path = data_path

    def get_data_path(self, *rel_path):
        """Returns a file path to a file stored in the data folder using one or more
        path components. Used internally
        """
        data_dir = os.path.join(self.data_path, *rel_path)
        return os.path.normpath(data_dir)

    def _validate_base_map(self, fname, basemap: DataMap, languages, error=True):
        languages_with_errors = set()
        for entry in basemap.values():
            # Validation prepass. Find missing languages in the new entry
            for lang in languages:
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
        
    def load_base_json(self, data_file, languages, validate=True):
        "Loads a base data map object. The data map must have unique name in the given languages"
        data_file = self.get_data_path(data_file)

        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)

        result = DataMap(languages=languages)
        for row in data:
            result.insert(row)

        if languages:
            self._validate_base_map(data_file, result, languages, error=validate)

        return result

    def load_keymap_csv(self, data_file, schema=None):
        """Loads a simple csv file as a key map. 
        The key column becomes the map's key, and every entry gets an id field (accessed via variable).
        TODO: Polish, might need an interface tweak to be similar to datamap"""
        items = self.load_list_csv(data_file)

        keymap = { entry['key']:entry for entry in items }
        if schema:
            keymap = apply_schema_to_map(keymap, schema)

        for idx, entry in enumerate(keymap.values()):
            entry.id = idx + 1 

        return keymap

    def load_base_csv(self, data_file, languages, groups=[], translation_filename=None, translation_extra=[], validate=True):
        """Loads a base data map object from a csv
        groups is a list of additional fields (name is automatically include)
        that nest via groupname_subfield.
        """
        data_file = self.get_data_path(data_file)
        groups = ['name'] + groups

        rows = read_csv(data_file)
        rows = [group_fields(row, groups=groups) for row in rows]

        basemap = DataMap(languages=languages)
        basemap.extend(rows)

        if translation_filename:
            dataitems = self.load_list_csv(translation_filename)
            if dataitems:
                groups = set(['name'] + translation_extra)
                
                # Get first column name, whose values will anchor the data to merge
                first_column_name = next(iter(dataitems[0].keys()))

                results = {}
                for item in dataitems:
                    key = item[first_column_name]

                    # Remove the join from the subdata
                    item.pop(first_column_name) 
                    
                    results[key] = group_fields(item, groups=groups)

                basemap.merge(results, key_join=first_column_name)

        if languages:
            self._validate_base_map(data_file, basemap, languages, error=validate)

        return basemap

    def load_data_json(self, parent_map : DataMap, data_file, *, key_join="name_en", key=None):
        """Loads a data file, using a base map to anchor it to id
        The parent_map is updated to map id -> data row.
        Returns the parent_map to support chaining
        """
        data_file = self.get_data_path(data_file)

        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)

        parent_map.merge(data, key_join=key_join, key=key)
        return parent_map

    def load_data_csv(self, parent_map : DataMap, data_file, *, key=None, groups=[], leaftype):
        """Loads a data file, using a base map to anchor it to id
        The parent_map is updated to map id -> data row.
        Returns the parent_map to support chaining.

        :param key: The dictionary key name in the base map to add the new data under. 
                    If none, it'll extend the current list
        :param groups: Additional fields in the data map to group together into one field based on suffix.
        :param leaftype: Either list or dict, deciding on whether the result of the new data should be a list or just a dict.
                         Use list if the data is one to many, or dict if its one to one

        Language is automatically determined by the name of the first column.
        """
        
        data_file = self.get_data_path(data_file)

        if leaftype == 'list' and not key:
            raise ValueError("key is required if leaftype is list")
        
        rows = read_csv(data_file)

        if not rows:
            return parent_map

        # Auto detect language / field
        first_column = next(iter(rows[0].keys()))
        match = re.match('(?:base_)?([a-zA-Z_]+)', first_column)
        if not match:
            raise Exception("First column needs to be a base_{field} or base_{field}_{lang} column")
        
        fieldname = match.group(1)
        data = unflatten(rows, nest=[first_column], groups=groups, leaftype=leaftype)

        return parent_map.merge(data, key=key, key_join=fieldname)
