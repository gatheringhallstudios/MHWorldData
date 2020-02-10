import typing
import collections
import copy
import re

import mhdata.typecheck as typecheck
import mhdata.util as util

def to_basic(obj, *, stack=[]):
    """Converts an object to its most basic form, recursively.
    Does not prevent infinite recursion, careful with usage.
    """
    obj_id = id(obj)
    if obj_id in stack:
        raise Exception("Cyclical reference detected")

    if isinstance(obj, collections.Mapping):
        # This can be converted to a dictionary
        return { k:to_basic(v, stack=stack+[obj_id]) for (k, v) in obj.items() }
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, collections.Iterable):
        return [to_basic(v, stack=stack+[obj_id]) for v in obj]
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

def derive_lang(field):
    if field in ['base_id', 'id']:
        return None
    
    match = re.match('(?:base_)?name_([a-zA-Z_]+)', field)
    if not match:
        raise Exception(f"Invalid column name {field}. " +
            "First column needs to be id, name_{lang} or base_name_{lang} column")
    return match.group(1)

def fix_id(rows: typing.Iterable[dict]):
    for row in rows:
        if 'id' in row: row['id'] = int(row['id'])
    return rows

def merge_list(base, rows: typing.Iterable[dict], key=None, groups=[], many=False):
    """Routine to merge lists of dictionaries together using one or more keys.
    The keys used are determined by first sequential key of the first row.
    If the key is an id, it will join on that, but if it is a name, it will join on that and key_ex fields.
    """
    def create_key_fields(data_map, column_name):
        lang = derive_lang(column_name)
        
        key_fields = []
        if lang is None:
            key_fields.append('id')
        else:
            key_fields.append(f'name_{lang}')
            key_fields.extend(data_map.keys_ex)

        return key_fields

    def create_key_fn(key_fields):
        def derive_key(dict):
            items = []
            for k in key_fields:
                if f'base_{k}' in dict:
                    items.append(dict[f'base_{k}'])
                else:
                    items.append(dict[k])
            return tuple(str(i) for i in items)
        return derive_key

    if many and not key:
        raise ValueError('Key must have a value')

    if not rows:
        return

    # Create keying function
    first_column = next(iter(rows[0].keys()))
    key_fields = create_key_fields(base, first_column)
    derive_key = create_key_fn(key_fields)

    # group rows
    keyed_data = {}
    for row in rows:
        row_key = derive_key(row)

        # Delete key fields. Its possible for base_name_en AND name_en to be in the same row.
        # Therefore, prioritize deleting base_ versions first
        for k in key_fields:
            if f'base_{k}' in row:
                del row[f'base_{k}']
            elif k in row:
                del row[k]
                
        if groups:
            row = util.group_fields(row, groups=groups)
        entry = keyed_data.setdefault(row_key, [])
        entry.append(row)
        if not many and len(entry) > 1:
            raise ValueError(f"Key {row_key} has too many matching entries in sub data")

    # Group base
    base = { derive_key(e):e for e in base.values() }
    "Test the keys to see that sub's keys exist in base"
    unlinked = [k for k in keyed_data.keys() if k not in base.keys()]
    if unlinked:
        raise Exception(
            "Several entries in sub data map cannot be joined. Their keys are " +
            ','.join('None' if e is None else str(e) for e in unlinked))

    for data_key, data_entries in keyed_data.items():
        base_entry = base[data_key]
        if key:
            if many:
                base_entry[key] = data_entries
            else:
                base_entry[key] = data_entries[0]
        elif isinstance(data_entries[0], collections.Mapping):
            util.joindicts(base_entry, data_entries[0])
        else:
            # We cannot merge a dictionary with a non-dictionary
            raise Exception("Invalid data, the data map must be a dictionary for a keyless merge")
