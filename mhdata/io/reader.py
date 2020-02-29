import os
import re
import collections.abc
import typing
import json
import re

from mhdata.util import ensure, ensure_warn

from .datamap import DataMap
from mhdata.util import group_fields
from .functions import merge_list, fix_id

from mhdata.io.csv import read_csv

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

    def load_json(self, data_file):
        data_file = self.get_data_path(data_file)
        with open(data_file, encoding="utf-8") as f:
            return json.load(f)
        
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

    def load_base_csv(self, data_file, languages, groups=[], translation_filename=None, translation_extra=[], keys_ex=[], validate=True):
        """Loads a base data map object from a csv
        groups is a list of additional fields (name is automatically include)
        that nest via groupname_subfield.
        """
        data_file = self.get_data_path(data_file)
        groups = ['name'] + groups

        rows = [group_fields(row, groups=groups) for row in read_csv(data_file)]

        basemap = DataMap(languages=languages, keys_ex=keys_ex)
        basemap.extend(rows)

        if translation_filename:
            try:
                translations = fix_id(self.load_list_csv(translation_filename))
                groups = set(['name'] + translation_extra)
                merge_list(basemap, translations, groups=groups, many=False)
            except FileNotFoundError:
                print(f"Warning: Could not find translation file {translation_filename}")
            except Exception as ex:
                raise Exception(f"Unknown error while reading file {data_file}") from ex

        if languages:
            self._validate_base_map(data_file, basemap, languages, error=validate)

        return basemap
