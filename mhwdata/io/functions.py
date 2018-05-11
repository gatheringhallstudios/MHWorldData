import typing
from .datamap import DataMap

def flatten(obj, base_obj={}, nest=[], groups=[]):
    "Flattens an object into a list of flat dictionaries"
    # This is a recursive algorithm, where we iteratively step through "nest levels"
    # until we run out, and then we process the groups.
    # Returns a list of all results for the object.

    if not nest:
        # return a single result. This is the "base" result (base case)
        result = dict(base_obj)
        for key, value in obj.items():
            if key not in groups:
                result[key] = value
                continue

            # This is a "group" item, so iterate over it
            for subkey, subvalue in value.items():
                result[f"{key}_{subkey}"] = subvalue

        return [result]

    else:
        # Return multiple results by stepping down one depth level,
        # and recursively calling it for the sub-items
        current_nest = nest[0]
        remaining_nest = nest[1:]

        results = []
        for nest_value, remaining_data in obj.items():
            sub_base_obj = dict(base_obj)
            sub_base_obj[current_nest] = nest_value
            
            sub_flattened = flatten(
                remaining_data, 
                base_obj=sub_base_obj,
                nest=remaining_nest,
                groups=groups)

            results.extend(sub_flattened)

        return results


def determine_fields(obj_list):
    """
    Returns the set of all possible keys in the object list
    """
    fields = []
    for obj in obj_list:
        for key in obj.keys():
            if key not in fields:
                fields.append(key)

    return fields

def group_fields(obj, groups=[]):
    "Returns a new dictionary where the items that start with groupname_ are consolidated"
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

def extract_sub_data(data_map : DataMap, *, root=None, fields=None, lang='en'):
    "Returns sub-data anchored by name. Similar to reversing DataMap.merge()"
    
    if not root and not fields:
        raise Exception(
            "Either a root (string or dictionary) " +
            "or a list of fields must be given when persisting a data map")

    result = {}

    root_is_string = isinstance(root, str)

    for entry_id, entry in data_map.items():
        name = entry.name(lang)

        # stores the result for this round
        result_entry = {}

        # If the root is a string, use the field as the entry (if it exists)
        # if the root field doesn't exist, skip to the next
        if root and root_is_string:
            if root not in entry:
                continue
            entry = entry[root]

        if fields:
            # If fields is given, always save them regardless of location
            for field in fields:
                if field not in entry:
                    continue
                result_entry[field] = entry[field]
        else:
            # check the fields in the entry to copy them over
            for key, value in entry.items():
                # if root is not a string, assume its a base map
                # If the field is part of the base map, then skip
                if root and not root_is_string:
                    base_entry = root[entry.id]
                    if key in base_entry:
                        continue

                result_entry[key] = value

        if result_entry:
            result[name] = result_entry

    return result