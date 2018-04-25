import click
import sys

from mhwdata.build import build_database

# Python 3.6 dictionaries preserve insertion order, and python 3.7 added it to the spec officially
# Older versions of python won't maintain order when importing data for the build.
if sys.version_info < (3,6):
    print(f"WARNING: You are running python version {sys.version}, " +
        "but this application was designed for Python 3.6 and newer. ")
    print("Earlier versions of Python will still build the project, but will not have a consistent build.")
    print("When creating a final build, make sure to use a newer version of python.")


@click.command()
def build():
    output_filename = 'mhw.db'
    build_database(output_filename)
    
if __name__ == '__main__':
    build()