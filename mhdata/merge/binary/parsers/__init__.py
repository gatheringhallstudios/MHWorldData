from .mib import *
from .epg import *

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