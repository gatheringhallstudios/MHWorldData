from collections.abc import MutableMapping, Mapping
import collections
import typing

class DataMapRow(MutableMapping):
    """Defines a single row of a datamap object.
    These objects are regular dictionaries that can also get translated names.
    """

    def __init__(self, translate_map, id : int, datarowdict: dict):
        self._translate_map = translate_map
        self._id = id
        self._data = datarowdict

    @property
    def id(self):
        "Returns the id associated with this DataMapRow"
        return self._id

    def name(self, lang_id):
        "Returns the name of this data map row in a specific language"
        return self._translate_map[self.id][lang_id]

    def names(self):
        "Returns a collection of (language, name) tuples for this row"
        return self._translate_map[self.id].items()

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

class DataMap(typing.Mapping[int, DataMapRow]):
    def __init__(self, translate_map, datadict: dict):
        """Constructs a new DataMap object. DataDict is an id->entry mapping.
        It is recommended to use a load function instead."""
        self._translate_map = translate_map

        # build keys. Keys need to be in translate map order, but contain our entries
        self._keys = []
        self._data = collections.OrderedDict()
        for key in translate_map.keys():
            data_row_raw = datadict.get(key, None)
            if data_row_raw:
                self._keys.append(key)
                self._data[key] = DataMapRow(translate_map, key, data_row_raw)

    def __getitem__(self, id) -> DataMapRow:
        return self._data[id]

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return self._keys.__iter__()

