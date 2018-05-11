import collections


def ensure(field, error_message):
    "Tests that the field is truthy, throwing an Exception if its not"
    if not field:
        raise Exception("ERROR: " + error_message)


def ensure_warn(field, error_message):
    "Tests that the field is truthy, printing a warning message if its not"
    if not field:
        print("WARNING: " + error_message)


def get_duplicates(iterable):
    "Checks the iterable for duplicate entries, and returns them"
    seen = set()
    duplicates = []
    for item in iterable:
        if item in seen:
            duplicates.append(item)
        else:
            seen.add(item)

    return duplicates


def joindicts(dest, *dictlist):
    """Merges one or more dictionaries into dest, without overwriting existing entries
    Returns the generated result.

    To merge with overwrite, use the native dict update method.
    """
    result = dest
    for d in dictlist:
        for key, value in d.items():
            if key not in result:
                result[key] = value
    return result


def extract_fields(obj : dict, *fieldnames) -> dict:
    result = {}
    for fieldname in fieldnames:
        if fieldname not in obj:
            continue
        result[fieldname] = obj[fieldname]
    return result


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


def is_flat_iterable(value):
    "Returns true if the object is a flat iterable (not a dictionary/string)"
    if isinstance(value, str) or isinstance(value, collections.Mapping):
        return False
    return isinstance(value, collections.Iterable)


def is_flat_dict(obj : dict) -> bool:
    "Returns true if the dictionary has only scalar values"
    return all({ is_scalar(v) for v in obj.values()})


def is_flat_dict_list(obj_list) -> bool:
    "Returns true if all dictionaries in the list have only scalar values"
    return all(( is_flat_dict(o) for o in obj_list))
