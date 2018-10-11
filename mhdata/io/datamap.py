import typing
import collections
import itertools
import copy

from collections.abc import Mapping, KeysView
from mhdata.util import joindicts, extract_fields

from .datarow import DataRow
from .functions import to_basic


class NameSet(KeysView):
    "A 'set-like' object for iterating over the names of a DataMap in a single language"
    def __init__(self, backing_data, language_code):
        self._map = backing_data
        self.language_code = language_code

    def __iter__(self):
        for row in self._map.values():
            yield row.name(self.language_code)

    def __contains__(self, key):
        if self._map.entry_of(self.language_code, key):
            return True
        return False


class DataMap(typing.Mapping[int, DataRow]):
    """A collection of data entries key'd by an id.

    Entries on this map can be retrieved using its id, or using its name in any language.
    To iterate over entries, use the values function.
    """

    def __init__(self, data: typing.Mapping[int, dict] = None):
        self._data = collections.OrderedDict()
        self._reverse_entries = {}

        # todo: replace id gen with the object index...maybe...
        self._id_gen = itertools.count(1)
        self._last_id = 0

        if data:
            for id, entry in data.items():
                self.add_entry(id, entry)

    def id_of(self, language_code, name):
        "Returns the id of the map entry that contains the code+value. Otherwise returns None"
        key = (language_code, name)
        return self._reverse_entries.get(key, None)

    def entry_of(self, language_code, name):
        "Returns the entry that contains the code+value, which can be used to get other languages. Otherwise none"
        id_value = self.id_of(language_code, name)
        return self._data.get(id_value, None)

    def _generate_id(self):
        entry_id = next(self._id_gen)
        self._last_id = entry_id
        return entry_id

    def _unregister_entry(self, entry):
        "Internal function to remove the entry from the reverse mapping"
        for lang, name in entry.names():
            if name is None: continue

            key = (lang, name)
            del self._reverse_entries[key]

    def _register_entry(self, entry):
        "Internal function add the entry to the reverse mapping"
        for lang, name in entry.names():
            if name is None: continue

            key = (lang, name)
            if key in self._reverse_entries:
                raise ValueError(f"Duplicate name ({lang}, {name}) in DataMap")
           
            self._reverse_entries[key] = entry.id

    def _add_entry(self, entry_id: int, entry: dict):
        "Internal: Adds an entry to the dict, and returns the entry"
        if 'name' not in entry:
            raise KeyError("An entry is missing a name value")

        if entry_id in self._data:
            raise KeyError(f"An entry with the given key already exists: {entry_id}")

        new_entry = DataRow(entry_id, entry)
        self._register_entry(new_entry)
        
        self._data[entry_id] = new_entry
        return new_entry

    def add_entry(self, entry_id: int, entry: dict):
        """"
        Adds an entry to the dict, and returns the entry.
        If this is higher than the last set id, reset the generator"""
        entry_id = int(entry_id)

        if 'id' in entry and entry['id'] != entry_id:
            raise ValueError("Mismatch in add_entry: entry already has an id")

        if isinstance(entry_id, int) and entry_id > self._last_id:
            self._id_gen = itertools.count(entry_id + 1)
            self._last_id = entry_id

        return self._add_entry(entry_id, entry)

    def insert(self, entry: dict):
        """Inserts a dictionary as a new entry
        
        If the entry has an id field, it is used (and changed to an int)
        Otherwise a new id is auto-generated.
        """
        if 'id' in entry:
            try:
                entry_id = int(entry['id'])
            except ValueError:
                raise ValueError("Entry id must be an int")
        else:
            entry_id = next(self._id_gen)
        return self._add_entry(entry_id, entry)

    def extend(self, entries: typing.List[dict]):
        for entry in entries:
            self.insert(entry)

    def names(self, language_code):
        "Returns a set like object of all the names in a given language"
        return NameSet(self, language_code)

    def to_dict(self):
        "Fully converts the data stored into a serializable dictionary, keyed by id"
        return to_basic(self)

    def to_list(self):
        "Fully converts the data entries stored into a serializable list"
        return to_basic(self.values())

    def copy(self):
        "Returns a new DataMap object with all fields cloned"
        clone_data = self.to_dict()
        return DataMap(clone_data)

    def merge(self, data, *, lang="en", key=None):
        """Merges a dictionary keyed by the names in a language to this data map
        
        If a key is given, it will be added under key,
        Otherwise it will be merged without overwrite.

        Returns self to support chaining.
        """
        # validation, make sure it links
        data_names = self.names(lang)
        unlinked = [key for key in data.keys() if key not in data_names]
        if unlinked:
            raise Exception(
                "Several invalid names found in sub data map. Invalid entries are " +
                ','.join(unlinked))

                # validation complete, it may not link to all base entries but thats ok
        for data_key, data_entry in data.items():
            base_entry = self.entry_of(lang, data_key)
            
            if key:
                base_entry[key] = data_entry
                
            elif isinstance(data_entry, collections.Mapping):
                if 'name' in data_entry:
                    self._unregister_entry(base_entry)
                    joindicts(base_entry, data_entry)
                    self._register_entry(base_entry)
                else:
                    joindicts(base_entry, data_entry)
                    
            else:
                # If we get here, its a key-less merge with a non-dict
                # We cannot merge a dictionary with a non-dictionary
                raise Exception("Invalid data, the data map must be a dictionary for a keyless merge")
            
        return self

    def extract(self, key=None, fields=None, lang='en'):
        "Returns sub-data anchored by name. Similar to reversing DataMap.merge()"
        
        if not key and not fields:
            raise ValueError(
                "Either a key or a list of fields " +
                "must be given when persisting a data map")

        result = {}

        for entry in self.values():
            name = entry.name(lang)

            # If root is supplied, nest. If doesn't exist, skip to next item
            if key:
                if not entry.get(key, None):
                    continue
                entry = entry[key]

            # If we re-rooted, we might be looking at a list now
            # Lists are extracted as-is
            # TODO: what if we get a list here and fields is supplied?
            if not isinstance(entry, collections.Mapping):
                result[name] = entry
                continue

            # If fields is given, extract them
            if fields:
                result[name] = extract_fields(entry, *fields)
            else:
                result[name] = copy.deepcopy(entry)

        return result
        
    def pop(self, entry_id, default=None):
        """If key is in the dictionary, remove it and return its value, else return default.
        If default is not given and key is not in the directory, KeyError is raised.
        """
        try:
            item = self[entry_id]
            del self[entry_id]
            return item
        except KeyError:
            if default is None:
                raise
            return default

    def __getitem__(self, id) -> DataRow:
        return self._data[id]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()

    def __delitem__(self, id):
        entry = self._data[id]
        del self._data[id]
        for lang, val in entry.names():
            del self._reverse_entries[(lang, val)]
