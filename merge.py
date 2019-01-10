import click
import sys

from mhdata.merge import mhwdb, binary

# todo: organize

if sys.version_info < (3,6):
    print("This application has designed for python 3.6 and later")
    exit(1)

@click.group()
def merge():
    "Commands to automatically merge data with external sources."

@merge.group(name="mhwdb")
def mhwdb_cmd():
    "Merges using mhwdb"

@merge.group(name="binary")
def binary_cmd():
    "Merge using ingame binaries"

@mhwdb_cmd.command()
def weapons():
    "Merges weapon data with results from LartTyler's MHWDB API"
    mhwdb.merge_weapons()

@binary_cmd.command()
def update():
    "Performs an update TODO: COMPLETE"
    binary.update_armor()
    binary.update_weapons()

if __name__ == '__main__':
    merge()