# The save methods are not part of the build process
# They are used whenever I am pulling new data from other sources.

import json
import collections
import os
import os.path
import copy

import mhdata.util as util
from .datamap import DataMap
from .reader import DataReader

from mhdata.util import ungroup_fields, typecheck, extract_fields
from mhdata.io.csv import save_csv

class DataReaderWriter(DataReader):
    "A data reader that can also be used to create and update data"

    def save_csv(self, location, rows, *, schema=None):
        "Saves a raw csv relative to the source data location"
        if schema:
            rows, errors = schema.dump(rows, many=True)
        location = self.get_data_path(location)
        save_csv(rows, location)

    def save_base_map(self, location, base_map):
        "Writes a data map to a location in the data directory"
        location = self.get_data_path(location)
        result = base_map.to_list()

        with open(location, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    def save_base_map_csv(self, location, base_map: DataMap, *, groups=['name'], schema=None, translation_filename=None, translation_extra=[], key_join='name_en'):
        """
        Saves a base map as a csv file.
        If a marshmallow schema is provided, groups is ignored. 
        The schema becomes in charge of flattening.
        """
        
        if 'name' not in groups:
            raise Exception("Name is a required group for base maps")

        # Write translation file
        if translation_filename:
            translations = []
            translation_fields = ['name'] + translation_extra
            for row in base_map.values():
                ex_values = { k:row[k] for k in base_map.keys_ex }
                translation_row = { key_join: row[key_join], **ex_values }
                for lang in self.languages:
                    for field in translation_fields:
                        field_key = f'{field}_{lang}'
                        if field_key in translation_row:
                            continue
                        value = row.get(field, {}).get(lang, '') or ''
                        translation_row[field_key] = value.strip()
                
                translations.append(translation_row)

                # Remove separated entries from base map
                # Removes all "extra group fields" and non-english name entries
                row['name'] = { 'en': row['name']['en'] }
                for field in translation_extra:
                    if field in row: del row[field]

            self.save_csv(translation_filename, translations)

        rows = base_map.to_list()

        if not schema:
            rows = [ungroup_fields(v, groups=groups) for v in rows]
        else:
            rows, errors = schema.dump(rows, many=True)

        self.save_csv(location, rows)

    def save_data_json(self, location, data_map, *, key=None, fields=None, key_join='name_en'):
        """Write a DataMap to a location in the data directory.

        If key is given, then the saving is restricted to what's inside that key.
        If fields are given, only fields within the list are exported.

        At least one of key or fields is required
        """
        location = self.get_data_path(location)
        result = data_map.extract(key=key, fields=fields, key_join=key_join)
        with open(location, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    def save_data_csv(self, location, data_map: DataMap, *,
            key_join='name_en',
            nest_additional=[],
            groups=[],
            key=None,
            fields=None,
            schema=None):
        """Write a DataMap to a location in the data directory.

        If key is given, then the saving is restricted to what's inside that key.
        If fields are given, only fields within the list are exported.

        At least one of key or fields is required.

        TODO: Write about nest_additional and groups
        """

        if not key and not fields:
            raise ValueError(
                "Either a key or a list of fields " +
                "must be given when persisting a data map")

        flattened_rows = []
        for entry in data_map.values():
            ex_values = { k:entry[k] for k in data_map.keys_ex }
            row_base = { 'base_' + key_join: entry[key_join], **ex_values }

            items = None
            if key and key in entry and entry[key]:
                items = entry[key]
                if not typecheck.is_flat_iterable(items):
                    items = [items]
            elif not key and fields:
                items = [entry.to_dict()]

            if not items:
                continue

            for item in items:
                # If fields is given, extract them
                if fields:
                    values = extract_fields(item, *fields)
                else:
                    values = copy.deepcopy(item)
                new_row = { **row_base, **values }
                flattened_rows.append(new_row)

        flattened_rows = [ungroup_fields(v, groups=groups) for v in flattened_rows]
        self.save_csv(location, flattened_rows, schema=schema)

    def save_keymap_csv(self, location, data: dict, schema=None):
        "Saves a dict as a csv, where the key becomes a value called key"
        data = [ { 'key': key, **value } for key, value in data.items() ]
        self.save_csv(location, data, schema=schema)
