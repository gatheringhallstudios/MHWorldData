import os
from os import path

import typing

import csv

def write_artifact(filename, *raw_data):
    """Writes an artifact file, 
    which is a temporary fakefile used to gauge game data
    """
    basepath = path.join(path.dirname(__file__), '../../../artifacts/')

    os.makedirs(basepath, exist_ok=True)
    with open(path.join(basepath, filename), 'w', encoding='utf8') as f:
        f.write('\n'.join(raw_data))

def write_names_artifact(filename, names: typing.Iterable[str]):
    """Writes an artifact file, which is a temporary fakefile used to examine game data. 
    Writes a list of names to the file"""
    # todo: remove, use write lines instead
    write_lines_artifact(filename, names)

def write_lines_artifact(filename, lines: typing.Iterable[str]):
    """Writes an artifact file, which is a temporary fakefile used to examine game data. 
    Writes a list of lines to the file"""
    write_artifact(filename, '\n'.join(lines))
