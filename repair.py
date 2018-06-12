import click
import sys

import mhdata.load as data
import mhdata.repair as repair_functions

from mhdata.io import DataReaderWriter

# Python 3.6 dictionaries preserve insertion order, and python 3.7 added it to the spec officially
# Older versions of python won't maintain order when importing data for the build.
if sys.version_info < (3,6):
    print(f"WARNING: You are running python version {sys.version}, " +
        "but this application was designed for Python 3.6 and newer. ")
    print("Earlier versions of Python will still build the project, but will not have a consistent build.")
    print("When creating a final build, make sure to use a newer version of python.")

@click.group()
def repair():
    "Contains subcommands to repair (aka reorder) certain data elements"
    pass

@repair.command()
def skills():
    "Reorders skill level details to match the base's data ordering"
    repair_functions.repair_skill_data()

@repair.command()
def armor():
    "Repairs all armor data to synchronize data order"
    repair_functions.repair_armor_data()

if __name__ == '__main__':
    repair()