class TranslateMap:
    """"
    Defines a dictionary mapping id to language_code+name bidirectionally
    Iterating returns TranslationMapEntry objects
    """
    
    def __init__(self):
        # key'd by id
        self._entries = {}

    def id_of(self, language_code, value):
        "Returns the id of the map entry that contains the code+value. Otherwise returns None"
        # note: this algorithm is brute force and slow. We can improve it later if we need to
        for entry in self._entries.values():
            if entry.get(language_code, None) == value:
                return entry.id
        return None

    def add_entry(self, id, language_code, value):
        entry = self._entries.get(id, None)
        if not entry:
            entry = TranslationMapEntry(id, self)
            self._entries[id] = entry
        entry[language_code] = value

    def names_for(self, language_code):
        """Returns a generator that can be used to iterate over the names of a single language.
        Skips null entries
        """
        return filter(lambda a: a, map(lambda e: e.get(language_code), self))

    def all_items(self):
        "Returns an exhaustive set of (id, language, name) pairs"
        for entry in self:
            for language, name in entry.items():
                yield (entry.id, language, name)

    def __getitem__(self, id):
        return self._entries[id]

    def __iter__(self):
        return self._entries.values().__iter__()
    
class TranslationMapEntry:
    def __init__(self, id, parent):
        self.id = id
        self.parent = parent
        self._translations = {}

    def __getitem__(self, code):
        return self._translations.__getitem__(code)

    def __setitem__(self, code, value):
        self._translations[code] = value

    def items(self):
        "Returns (language, name) tuples"
        return self._translations.items()

    def get(self, code, d=None):
        try:
            return self._translations[code]
        except KeyError:
            return d
