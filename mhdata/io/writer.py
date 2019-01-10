# The save methods are not part of the build process
# They are used whenever I am pulling new data from other sources.

import json
import collections
import os
import os.path

import mhdata.util as util
from .datamap import DataMap
from .reader import DataReader

from .functions import flatten
from mhdata.util import ungroup_fields
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

    def save_base_map_csv(self, location, base_map, *, groups=['name'], schema=None, translation_filename=None, translation_extra=[]):
        """
        Saves a base map as a csv file.
        If a marshmallow schema is provided, groups is ignored. 
        The schema becomes in charge of flattening.
        """
        
        if 'name' not in groups:
            raise Exception("Name is a required group for base maps")

        rows = base_map.to_list()

        if translation_filename:
            translations = []
            translation_fields = ['name'] + translation_extra
            for row in rows:
                translation_row = {}
                for lang in self.languages:
                    for field in translation_fields:
                        value = row[field].get(lang, '') or ''
                        translation_row[f'{field}_{lang}'] = value.strip()
                
                translations.append(translation_row)

                row['name'] = { 'en': row['name']['en'] }
                for field in translation_extra:
                    del row[field]

            self.save_csv(translation_filename, translations)

        if not schema:
            rows = [ungroup_fields(v, groups=groups) for v in rows]
        else:
            rows, errors = schema.dump(rows, many=True)

        self.save_csv(location, rows)

    def save_data_json(self, location, data_map, *, key=None, fields=None, lang='en'):
        """Write a DataMap to a location in the data directory.

        If key is given, then the saving is restricted to what's inside that key.
        If fields are given, only fields within the list are exported.

        At least one of key or fields is required
        """
        location = self.get_data_path(location)
        result = data_map.extract(key=key, fields=fields, lang=lang)
        with open(location, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    def save_data_csv(self, location, data_map, *,
            lang='en',
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
        extracted = data_map.extract(key=key, fields=fields, lang=lang)
        flattened_rows = flatten(extracted, nest=['base_name_'+lang] + nest_additional)
        flattened_rows = [ungroup_fields(v, groups=groups) for v in flattened_rows]

        self.save_csv(location, flattened_rows, schema=schema)

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
