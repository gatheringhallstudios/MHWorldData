"""
Module used for loading data from the source_data/ folder. 
This module can read and write data to and from the source_data/ folder,
validate the data, and do postprocessing.

Use load_data to load the source data as is, or load_data_processed
to perform post processing and validation. Use the datafn submodule's
collection of helper functions to better read this data.
"""

from .loaddata import load_data
from .validate import validate

def load_data_processed():
    "Loads data from source_data/ folder, and validates and post-processes it"
    from . import process

    mhdata = load_data()
    process.copy_skill_descriptions(mhdata.skill_map)
    process.extend_decoration_chances(mhdata.decoration_map)

    if not validate(mhdata):
        raise Exception("Validation Failed")

    return mhdata