import click
import sys

from mhdata.merge import mhwdb

# todo: organize

if sys.version_info < (3,6):
    print("This application has designed for python 3.6 and later")
    exit(1)

@click.group()
def merge():
    "Commands to automatically merge data with external sources."

@merge.command()
def weapons():
    "Merges weapon data with results from LartTyler's MHWDB API"
    mhwdb.merge_weapons()


if __name__ == '__main__':
    merge()