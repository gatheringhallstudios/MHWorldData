import typing
import collections
import copy

import mhdata.typecheck as typecheck
import mhdata.util as util

def to_basic(obj, *, collected={}):
    """Converts an object to its most basic form, recursively.
    Does not prevent infinite recursion, careful with usage.
    """
    if isinstance(obj, collections.Mapping):
        # This can be converted to a dictionary
        return { k:to_basic(v) for (k, v) in obj.items()}
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, collections.Iterable):
        return [to_basic(v) for v in obj]
    else:
        return obj


def flatten(obj, *, nest, prefix={}):
    """Flattens a nested object into a list of flat dictionaries
    nest is a list of fieldnames.
    Do not use prefix, its internal.
    """
    # This is a recursive algorithm. 
    # We iteratively step through "nest levels".

    # BASE CASE
    if not nest:
        items = obj
        if not typecheck.is_flat_iterable(obj):
            items = [obj]

        # Error checking, items must be dictionaries
        if any(not typecheck.is_dict(item) for item in items):
            raise TypeError("Flattened entries must be a mapping type")
        
        # Extend all items with the prefix and return them
        return [{**prefix, **item} for item in items]

    # Validation
    if not isinstance(obj, collections.Mapping):
        raise ValueError("Object is not sufficiently deep for flattening")

    # Return multiple results by stepping down one depth level,
    # and recursively calling it for the sub-items
    current_nest = nest[0]
    remaining_nest = nest[1:]

    results = []
    for nest_value, remaining_data in obj.items():
        sub_prefix = { **prefix, current_nest: nest_value }
        
        # RECURSIVE CALL
        sub_flattened = flatten(remaining_data, nest=remaining_nest, prefix=sub_prefix)
        results.extend(sub_flattened)

    return results


def unflatten(obj_list, *, nest, groups=[], leaftype):
    """Performs the reverse of flatten. 
    Turns a CSV (list of objects) into a nested object.

    Nest is a list of fields used to walk through the nesting.

    TODO: Remove groups and leaftype and leave that to a post-step.
    Wait to see what the post-load abstraction will be before doing that.
    """
    if leaftype not in ['list', 'dict']:
        raise Exception("Unsupported leaf type")

    # This is a recursive algorithm
    if not nest:
        # BASE CASE: nothing more to nest, performs groups on entries
        if leaftype is 'list':
            return [util.group_fields(obj, groups=groups) for obj in obj_list]
        if leaftype is 'dict':
            return util.group_fields(obj_list[0], groups=groups)

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
