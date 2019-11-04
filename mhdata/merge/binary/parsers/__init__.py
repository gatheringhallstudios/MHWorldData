"""
Module used to parse binary data and read them into objects.
Handles certain types not handled by the ftypes folder of the mhw_armor_edit project.

This is only used to read data into objects.
Actual data crossreferencing is handled by other modules.
"""

from .mib import *
from .epg import *
from .itlot import *
from .structreader import read_struct_from_file, StructReader

def struct_to_json(obj):
    "Recursively serializes a binary to "
    from mhdata import typecheck

    if hasattr(obj, 'as_dict'):
        obj = obj.as_dict()

    if typecheck.is_dict(obj):
        return { key:struct_to_json(value) for key,value in obj.items() }
    elif typecheck.is_flat_iterable(obj):
        return [ struct_to_json(value) for value in obj ]
    
    return obj