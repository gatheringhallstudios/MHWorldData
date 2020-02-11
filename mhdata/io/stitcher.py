import json
import os.path
import collections.abc

from mhdata.util import joindicts, extract_fields, group_fields
from .datamap import DataMap
from .reader import DataReader
from .functions import merge_list, fix_id

class DataStitcher:
    """Dynamically creates an object by attaching data to a base object
    Methods in this class chain to each other.

    Common concepts:
     - key - If given, the added data will be added as entry[keyname] = yourdata.

     - groups - If you have defense_base and defense_map, you can use group defense
                to join them together as defense: { base: val, max: val}.
                Not necessary if a schema is provided to get() that handles it.
    """

    def __init__(self, reader: DataReader, *, use_id=False, dir='', keys_ex=[]):
        self.reader = reader
        self.dir = dir
        self.keys_ex = keys_ex or []
        self._data_map = None
        self.languages = [] if use_id else ['en']

        self._base_fname = None
        self._base_groups = None
        self._base_translate_fname = None
        self._base_translate_groups = []

    def _get_filename(self, filename):
        "Gets a filename relative to the internal dir, if any."
        if self.dir:
            return os.path.join(self.dir, filename)
        return filename

    @property
    def data_map(self):
        if self._data_map:
            return self._data_map

        if not self._base_fname:
            raise Exception("Data Map uninitialized, use base_csv function first")

        self._data_map = self.reader.load_base_csv(
            self._base_fname,
            self.languages,
            groups=self._base_groups,
            translation_filename=self._base_translate_fname,
            translation_extra=self._base_translate_groups,
            keys_ex=self.keys_ex)

        return self._data_map

    def use_base(self, data_map: DataMap):
        self._data_map = data_map
        return self

    def base_csv(self, data_file, *, groups=[]):
        """Sets the base map from a CSV file, and return self"""
        self._base_fname = self._get_filename(data_file)
        self._base_groups = groups
        return self

    def translate(self, filename, *, groups=[]):
        self._base_translate_fname = self._get_filename(filename)
        self._base_translate_groups = groups

        return self

    def add_json(self, data_file, *, key=None, join=None):
        """
        Loads a data map from a json file, adds it to the base map, and returns self.
        
        If a key is given, it will be added under key, 
        Otherwise it will be merged without overwrite.
        """

        if not join:
            raise ValueError('Join must have a value')

        data = self.reader.load_json(self._get_filename(data_file))

        def derive_key(d):
            return d[join]

        # validation, make sure it links
        entry_map = { str(e[join]):e for e in self.data_map.values() }
        converted_keys = [str(k) for k in data.keys()]
        unlinked = [k for k in converted_keys if k not in entry_map.keys()]
        if unlinked:
            raise Exception(
                "Several invalid names found in sub data map. Invalid entries are " +
                ','.join('None' if e is None else str(e) for e in unlinked))

        # validation complete, it may not link to all base entries but thats ok
        for data_key, data_entry in data.items():
            base_entry = entry_map[str(data_key)]
            
            if key:
                base_entry[key] = data_entry
                
            elif isinstance(data_entry, collections.Mapping):
                joindicts(base_entry, data_entry)
                    
            else:
                # If we get here, its a key-less merge with a non-dict
                # We cannot merge a dictionary with a non-dictionary
                raise Exception("Invalid data, the data map must be a dictionary for a keyless merge")

        return self

    def add_csv(self, data_file, *, key=None, groups=[]):
        """Loads a data map from a csv file, adds to the base map, and returns self.
        
        :param key: The dictionary key name in the base map to add the new data under. 
                    This field is required
        :param groups: Additional fields in the data map to group together into one field based on suffix.
        
        Data loaded through this method are joined and available as a list.
        """
        if not key:
            raise ValueError('Key must have a value')

        data_file = self._get_filename(data_file)
        rows = fix_id(self.reader.load_list_csv(data_file))
        merge_list(self.data_map, rows, key=key, groups=groups, many=True)

        return self

    def add_csv_ext(self, data_file, *, key=None, groups=[]):
        """Loads a data map from a csv file, adds to the base map (1-1), and returns self.
        
        Data loaded through this method are joined one to one and available as a dictionary.

        If a key is given, it will be added under key, 
        Otherwise it will be merged without overwrite.
        """

        data_file = self._get_filename(data_file)
        rows = fix_id(self.reader.load_list_csv(data_file))
        merge_list(self.data_map, rows, key=key, many=False)

        return self
    
    def get(self, *, schema=None):
        """Returns the stiched result. 
        If schema is provided, returns the items run through the marshmallow schema
        """
        if schema:
            results = DataMap(languages=self.languages, keys_ex=self.keys_ex)
            for entry in self.data_map.values():
                data = entry.to_dict()
                (converted, errors) = schema.load(data, many=False) # converted

                if errors:
                    name = entry.name('en')
                    raise Exception(f"Error loading {name}: {str(errors)}")

                # id may have changed type or value:
                # get the converted id before the original,
                # but default to original if missing or falsey
                entry_id = converted.get('id', None) or entry.id

                results.add_entry(entry_id, converted)
                
            return results

        return self.data_map
