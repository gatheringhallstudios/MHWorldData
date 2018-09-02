"""
A module containing typecheck functions.

Python uses duck typing to the point where certain checks can fulfill multiple conditions.
For example, strings are iterable, and is difficult to distinguish from lists.

This module contains such functions.
"""

import collections

def is_scalar(value):
    "Returns true if the value is a string, number, or null"
    if value is None:
        return True
    if isinstance(value, str):
        return True

    try:
        float(value)
        return True
    except:
        return False


def is_list(value):
    "Returns true if the object is an iterable that isn't a scalar"
    if is_scalar(value):
        return False
    return isinstance(value, collections.Iterable)


def is_flat_iterable(value):
    "Returns true if the object is a flat iterable (not a dictionary/string)"
    if isinstance(value, str) or isinstance(value, collections.Mapping):
        return False
    return isinstance(value, collections.Iterable)


def is_flat_dict(obj : dict) -> bool:
    "Returns true if the dictionary has only scalar values"
    if not isinstance(obj, collections.Mapping):
        raise Exception("obj is not a dictionary")
    return all({ is_scalar(v) for v in obj.values()})


def is_flat_dict_list(obj_list) -> bool:
    "Returns true if all dictionaries in the list have only scalar values"
    return all(( is_flat_dict(o) for o in obj_list))
