"""
A module that contains methods used to interact with the source data.

The DataMap is a class that can store a list of named objects, and
auto generates ids for the individual entries. The named entries
can be reverse looked up by any language string.

The DataReader and DataReaderWriter work by loading and saving DataMaps
to and from files. They must be given a source folder to work with, 
which in this project is usually the source_data folder.
"""

from .reader import DataReader
from .writer import DataReaderWriter
from .stitcher import DataStitcher

from .datamap import DataMap, DataRow