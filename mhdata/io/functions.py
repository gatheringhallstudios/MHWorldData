import typing
from collections import abc
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

    if isinstance(obj, abc.Mapping):
        # This can be converted to a dictionary
        return { k:to_basic(v, stack=stack+[obj_id]) for (k, v) in obj.items() }
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, abc.Iterable):
        return [to_basic(v, stack=stack+[obj_id]) for v in obj]
    else:
        return obj

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
        elif isinstance(data_entries[0], abc.Mapping):
            util.joindicts(base_entry, data_entries[0])
        else:
            # We cannot merge a dictionary with a non-dictionary
            raise Exception("Invalid data, the data map must be a dictionary for a keyless merge")
