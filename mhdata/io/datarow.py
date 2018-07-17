from collections.abc import MutableMapping
from .functions import to_basic

class DataRow(MutableMapping):
    """Defines a single row of a datamap object.
    These objects are regular dictionaries that can also get translated names.
    """

    def __init__(self, id: int, datarowdict: dict):
        self._data = { 'id': id, **datarowdict }

    @property
    def id(self):
        "Returns the id associated with this DataRow"
        return self['id']

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
