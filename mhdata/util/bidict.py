class bidict(dict):
    """A dictionary that behaves like a normal one, 
    with an additional reverse() method that can be used for opposite associations
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reverse_map = {}

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._reverse_map[value] = key

    def reverse(self):
        return self._reverse_map

    def __delitem__(self, key):
        self._reverse_map[self[key]]