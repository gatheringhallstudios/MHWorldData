import json
from mhwdata.util import joindicts

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
        self.data_map.merge(data, lang=self.join_lang, key=key)
        return self

    def get(self):
        return self.data_map