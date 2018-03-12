class DataMap:
    def __init__(self, translate_map, datadict: dict):
        """Constructs a new DataMap object. DataDict is an id->entry mapping.
        It is recommended to use a load function instead."""
        self._translate_map = translate_map
        self._data = datadict

        shared_items = set(datadict.keys()) & set(translate_map.keys())
        self._len = len(shared_items)

    def __getitem__(self, id):
        return self._data[id]

    def __len__(self):
        return self._len

    def items(self):
        """Iterates over the map as (id, row) entries.
        Ordering is decided by the translate map order.
        """
        for item in self._translate_map:
            item_id = item.id
            data_row = self._data.get(item_id, 0)
            if data_row:
                yield (item_id, data_row)

    def keys(self):
        for id, value in self.items():
            yield id

    def values(self):
        for id, value in self.items():
            yield value

    def get(self, id, d=None):
        try:
            return self._data[id]
        except KeyError:
            return d


