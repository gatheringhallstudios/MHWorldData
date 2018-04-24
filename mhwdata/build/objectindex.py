import itertools

class ObjectIndex:
    """An object used to generate unique ids for unique objects
    Only supports immutable objects, and dictionaries with an "items" method.
    """

    def __init__(self):
        self._sequence = itertools.count(1)
        self._registry = {}
        self._new_handlers = []

    def on_new(self):
        """Decorator to register a callback to new insertions. 
        Callback must accept an id and an object"""
        def deco(fn):
            self._new_handlers.append(fn)
            return fn
        return deco

    def id(self, obj, *, on_new=None):
        """"Returns the id registered to the object if exists,
        or returns a new id and registers the object.
        
        Supply a function to on_new to execute some code if its a new entry.
        The function should take two parameters, the new id and the object.
        """
        key = obj
        if hasattr(obj, 'items'):
            key = frozenset(obj.items())

        try:
            return self._registry[key]
        except KeyError:
            new_id = next(self._sequence)
            self._registry[key] = new_id
            self._newest = new_id

            if on_new:
                on_new(new_id, obj)

            for handler in self._new_handlers:
                handler(new_id, obj)
            
            return new_id
