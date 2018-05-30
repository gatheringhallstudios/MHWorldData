import typing
import collections
import itertools

from collections.abc import MutableMapping, Mapping, KeysView
from mhdata.util import joindicts

def to_basic(obj, *, collected={}):
    """Converts an object to its most basic form, recursively.
    Does not prevent infinite recursion, careful with usage.
    """
    if isinstance(obj, collections.Mapping):
        # This can be converted to a dictionary
        return { k:to_basic(v) for (k, v) in obj.items()}
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, collections.Iterable):
        return [to_basic(v) for v in obj]
    else:
        return obj


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


class DataRow(MutableMapping):
    """Defines a single row of a datamap object.
    These objects are regular dictionaries that can also get translated names.
    """

    def __init__(self, id: int, datarowdict: dict):
        self._id = id
        self._data = datarowdict

    @property
    def id(self):
        "Returns the id associated with this DataRow"
        return self._id

    def name(self, lang_id):
        "Returns the name of this data map row in a specific language"
        return self['name'][lang_id]

    def names(self):
        "Returns a collection of (language, name) tuples for this row"
        for (lang, name) in self['name'].items():
            yield (lang, name)

    def set_value(self, key, value, *, after=""):
        """"Sets a value in this dictionary.
        Same as using [key]=value, but allows an item to be placed after another"""
        if not after:
            self[key] = value
            return

        keys_to_move = []
        found_item = False
        for item_key in self._data.keys():
            if found_item:
                keys_to_move.append(item_key)
            elif item_key == after:
                found_item = True

        self[key] = value

        # Move every entry to the end of the list
        for item_key in keys_to_move:
            value = self._data[item_key]
            del self._data[item_key]
            self._data[item_key] = value

    def to_dict(self):
        return to_basic(self)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return self._data.__len__()

    def __repr__(self):
        # Show the repr of the shallow copy
        return repr({ k:v for (k, v) in self.items()})


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

    def _add_entry(self, entry_id, entry: dict):
        "Internal: Adds an entry to the dict, and returns the entry"
        if 'name' not in entry:
            raise KeyError("An entry is missing a name value")

        if entry_id in self._data:
            raise KeyError(f"An entry with the given key already exists: {entry_id}")

        new_entry = DataRow(entry_id, entry)
        for lang, name in new_entry.names():
            self._reverse_entries[(lang, name)] = entry_id
        self._data[entry_id] = new_entry
        return new_entry

    def add_entry(self, entry_id, entry: dict):
        """"
        Adds an entry to the dict, and returns the entry.
        If this is higher than the last set id, reset the generator"""

        if 'id' in entry and entry['id'] != entry_id:
            raise ValueError("Mismatch in add_entry: entry already has an id")

        if isinstance(entry_id, int) and entry_id > self._last_id:
            self._id_gen = itertools.count(entry_id + 1)
            self._last_id = entry_id

        return self._add_entry(entry_id, entry)

    def insert(self, entry: dict):
        """Inserts a dictionary as a new entry
        
        If the entry has an id field, it is used.
        Otherwise a new id is auto-generated.
        """
        if 'id' in entry:
            entry_id = entry['id']
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
                "Several invalid names found. Invalid entries are " +
                ','.join(unlinked))

                # validation complete, it may not link to all base entries but thats ok
        for data_key, data_entry in data.items():
            base_entry = self.entry_of(lang, data_key)
            
            if key:
                base_entry[key] = data_entry
            elif hasattr(data_entry, 'keys'):
                joindicts(base_entry, data_entry)
            else:
                # If we get here, its a key-less merge with a non-dict
                # We cannot merge a dictionary with a non-dictionary
                raise Exception("Invalid data, the data map must be a dictionary for a keyless merge")
            
        return self

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
