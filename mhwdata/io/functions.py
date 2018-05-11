import typing
import collections
import copy

import mhwdata.util as util
from .datamap import DataMap

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

def is_scalar(value):
    "Returns true if the value is a string or number"
    if value is None:
        return True
    if isinstance(value, str):
        return True

    try:
        float(value)
        return True
    except:
        return False

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

def flatten(obj, base_obj={}, nest=[], groups=[]):
    "Flattens an object into a list of flat dictionaries"
    # This is a recursive algorithm, where we iteratively step through "nest levels"
    # until we run out, and then we process the groups.
    # Returns a list of all results for the object.

    if not nest:
        # BASE CASE: We can receive either a list or dict here.
        # If its a dict, make it a list of one item to handle all cases
        items = obj
        if isinstance(obj, collections.Mapping):
            items = [obj]

        result = []
        for item in items:
            row = { **base_obj, **ungroup_fields(item, groups=groups) }
            if any({ not is_scalar(v) for v in row.values()}):
                raise Exception(
                    "Failed to flatten, found non-scalar value. " +
                    f"base nest object is {base_obj}")
            result.append(row)
        
        return result

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

def unflatten(obj_list, *, nest=[], groups=[], leaftype):
    """Performs the reverse of flatten. 

    Nest decides how deep the dictionary should go. 
    If the nest field doesn't exist, it throws an error.

    Note: It consolidates to a list. Consolidating to a dict will be a later update
    
    """
    if leaftype not in ['list', 'dict']:
        raise Exception("Unsupported leaf type")

    # This is a recursive algorithm
    if not nest:
        # BASE CASE: nothing more to nest, performs groups on entries
        if leaftype is 'list':
            return [group_fields(obj, groups=groups) for obj in obj_list]
        if leaftype is 'dict':
            return group_fields(obj_list[0], groups=groups)

    else:
        current_nest = nest[0]
        remaining_nest = nest[1:]

        # Phase one, start grouping rows
        grouped_rows = {}
        for mapping in obj_list:
            key = mapping.pop(current_nest)
            grouped_rows.setdefault(key, []).append(mapping)

        # Phase 2, unflatten recursively
        results = {}
        for key, items in grouped_rows.items():
            # Validation. Make sure it recurses correctly
            if leaftype != 'list' and len(items) > 1:
                raise Exception(
                    f"Found multiple entries for {current_nest}:{key}, " +
                    "which is invalid in this leaf type")

            # Recursive call
            results[key] = unflatten(
                items, 
                nest=remaining_nest, 
                groups=groups, 
                leaftype=leaftype)

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


def extract_sub_data(data_map : DataMap, *, key=None, fields=None, lang='en'):
    "Returns sub-data anchored by name. Similar to reversing DataMap.merge()"

    if not key and not fields:
        raise ValueError(
            "Either a key or a list of fields " +
            "must be given when persisting a data map")

    result = {}

    for entry in data_map.values():
        name = entry.name(lang)

        # If root is supplied, nest. If doesn't exist, skip to next item
        if key:
            if not entry.get(key, None):
                continue
            entry = entry[key]

        # If we re-rooted, we might be looking at a list now
        # Lists are extracted as-is
        # TODO: what if we get a list here and fields is supplied?
        if not isinstance(entry, collections.Mapping):
            result[name] = entry
            continue

        # If fields is given, extract them
        if fields:
            result[name] = util.extract_fields(entry, *fields)
        else:
            result[name] = copy.deepcopy(entry)

    return result
