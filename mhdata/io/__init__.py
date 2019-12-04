"""
A module that contains methods used to perform IO operations on the source data.

The DataMap is a data structure that can store a list of named objects,
auto generating ids for the individual entries. The named entries
can be reverse looked up by any language string, provided it is a keyed language.

The DataReader and DataReaderWriter work by loading and saving DataMaps
to and from files. They must be given a source folder to work with, 
which in this project is usually the source_data folder.
"""

from .reader import DataReader
from .writer import DataReaderWriter
from .stitcher import DataStitcher

from .datamap import DataMap, DataRow

def create_reader():
    "Creates a DataReader with default settings"
    from mhdata import cfg
    import os
    from os.path import dirname, abspath, join

    current_dir = dirname(abspath(__file__))
    return DataReader(
        languages=list(cfg.supported_languages), 
        data_path=join(current_dir, '../../source_data')
    )

def create_writer():
    "Creates a DataReader with default settings"
    from mhdata import cfg
    import os
    from os.path import dirname, abspath, join

    current_dir = dirname(abspath(__file__))
    return DataReaderWriter(
        languages=list(cfg.supported_languages), 
        data_path=join(current_dir, '../../source_data')
    )
