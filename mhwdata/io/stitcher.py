import json
from mhwdata.util import joindicts
from .datamap import DataMap
from .reader import DataReader

class DataStitcher:
    """Dynamically creates an object by attaching data to a base object
    Methods in this class chain to each other
    """

    def __init__(self, reader: DataReader, data_map: DataMap, *, join_lang='en'):
        self.reader = reader
        self.data_map = data_map
        self.join_lang = join_lang

    def add_json(self, data_file, *, key=None):
        """
        Loads a data map from a json file, adds it to the base map, and returns self.
        
        If a key is given, it will be added under key, 
        Otherwise it will be merged without overwrite.
        """

        self.reader.load_data_json(
            parent_map=self.data_map, 
            data_file=data_file, 
            lang=self.join_lang, 
            key=key)

        return self

    def add_csv(self, data_file, *, key=None, groups=[]):
        """Loads a data map from a csv file, adds to the base map, and returns self.
        
        Data loaded through this method are joined and available as a list.

        If a key is given, it will be added under key, 
        Otherwise it will be merged without overwrite.
        """

        self.reader.load_data_csv(
            parent_map=self.data_map, 
            data_file=data_file, 
            lang=self.join_lang, 
            key=key,
            groups=groups,
            leaftype="list")

        return self

    def add_csv_ext(self, data_file, *, key=None, groups=[]):
        """Loads a data map from a csv file, adds to the base map (1-1), and returns self.
        
        Data loaded through this method are joined one to one and available as a dictionary.

        If a key is given, it will be added under key, 
        Otherwise it will be merged without overwrite.
        """

        self.reader.load_data_csv(
            parent_map=self.data_map, 
            data_file=data_file, 
            lang=self.join_lang, 
            key=key,
            groups=groups,
            leaftype="dict")

        return self
    
    def get(self):
        return self.data_map