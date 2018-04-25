import json
from mhwdata.util import joindicts
from .functions import validate_key_join

class DataStitcher:
    """Dynamically creates an object by attaching data to a base object
    Methods in this class chain to each other
    """

    def __init__(self, reader, data_map, *, join_lang='en'):
        self.reader = reader
        self.data_map = data_map
        self.join_lang = join_lang

    def add_json(self, data_file, *, key=None):
        """
        Loads a data map from a json file, adds it to the base map, and returns self.
        
        If a key is given, it will be added under key, 
        Otherwise it will be merged without overwrite.
        """

        data_file = self.reader.get_data_path(data_file)
        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)

        return self.add_data(data, key=key)

    def add_data(self, data, *, key=None):
        """Adds data to the base map and returns self.

        If a key is given, it will be added under key, 
        Otherwise it will be merged without overwrite.
        """
        # validation, make sure it links
        unlinked = validate_key_join(self.data_map, data.keys(), join_lang=self.join_lang)
        if unlinked:
            raise Exception(
                "Several invalid names found. Invalid entries are " +
                ','.join(unlinked))


        # validation complete, it may not link to all base entries but thats ok
        for data_key, data_entry in data.items():
            base_entry = self.data_map.entry_of(self.join_lang, data_key)
            
            if key:
                base_entry[key] = data_entry
            elif hasattr(data_entry, 'keys'):
                joindicts(base_entry, data_entry)
            else:
                # If we get here, its a key-less merge with a non-dict
                # We cannot merge a dictionary with a non-dictionary
                raise Exception("Invalid data, the data map must be a dictionary for a keyless merge")
            
        return self

    def get(self):
        return self.data_map