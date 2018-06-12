import collections
from . import typecheck

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

def check_not_grouped(obj, groups):
    "Checks if any fields have already been grouped, and returns the ones that aren't"
    results = []
    for group in groups:
        if group in obj and isinstance(obj[group], collections.Mapping):
            continue
        results.append(group)
    return results


def group_fields(obj, groups=[]):
    "Returns a new dictionary where the items that start with groupname_ are consolidated"
    if not typecheck.is_list(groups):
        raise TypeError("groups needs to be a list or tuple")
    
    groups = check_not_grouped(obj, groups)
    result = {}
    for key, value in obj.items():
        group_results = list(filter(lambda g: key.startswith(g+'_'), groups))
        if not group_results:
            result[key] = value
            continue

        group_name = group_results[0]
        subkey = key[len(group_name)+1:]
        
        group = result.setdefault(group_name, {})
        group[subkey] = value

    return result


def ungroup_fields(obj, groups=[]):
    "Returns a new dictionary where keys that are in group are flattened"
    result = {}
    for key, value in obj.items():
        if key not in groups:
            result[key] = value
            continue

        # This is a "group" item, so iterate over it
        for subkey, subvalue in value.items():
            result[f"{key}_{subkey}"] = subvalue

    return result
