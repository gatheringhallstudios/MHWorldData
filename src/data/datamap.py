import typing
import collections

from collections.abc import MutableMapping, Mapping, KeysView

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

    def __init__(self, id : int, datarowdict: dict):
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

class DataMap(typing.Mapping[int, DataRow]):
    def __init__(self, data : typing.Mapping[int, dict] = None):
        self._data = collections.OrderedDict()
        self._reverse_entries = {}

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

    def add_entry(self, id, entry : dict):
        "Adds an entry to the dict, and returns the entry"
        if 'name' not in entry:
            raise KeyError("An entry is missing a name value")

        if id in self.keys():
            raise KeyError("An entry with the given id already exists")

        new_entry = DataRow(id, entry)
        for lang, name in new_entry.names():
            self._reverse_entries[(lang, name)] = id       
        self._data[id] = new_entry
        return new_entry

    def names(self, language_code):
        "Returns a set like object of all the names in a given language"
        return NameSet(self, language_code)

    def __getitem__(self, id) -> DataRow:
        return self._data[id]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()