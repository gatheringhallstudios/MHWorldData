import typing
from .datamap import DataMap

def validate_key_join(data_map : DataMap, keys : typing.Set, *, join_lang='en'):
    """Validates if the set of keys can be joined to the data map.
    
    Returns a list of violations on failure

    When a data map is merging to a base map, all of the keys in the data map
    must exist as names in the base map. Any key that is missing in the base map
    is not mergable and is usually the result of a user error."""
    data_names = data_map.names(join_lang)
    return [key for key in keys if key not in data_names]
