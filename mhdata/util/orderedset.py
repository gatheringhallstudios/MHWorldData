import collections.abc

class OrderedSet(collections.abc.MutableSet):
    "A set that maintains insertion order"

    def __init__(self):
        # use a dict to hold data. 
        # In python 2.6 and up, dicts maintain insertion order
        self._data = {}

    def add(self, item):
        if item not in self:
            self._data[item] = 1

    def discard(self, item):
        if item in self:
            del self._data[item]

    def __contains__(self, item):
        return item in self._data

    def __iter__(self):
        return self._data.keys().__iter__()

    def __len__(self):
        return len(self._data)

