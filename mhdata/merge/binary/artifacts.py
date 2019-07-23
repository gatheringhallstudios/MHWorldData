import os
from os import path

import typing

from mhdata import typecheck
from mhdata.io.csv import save_csv

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

def write_dicts_artifact(filename, lines: typing.Iterable[dict], autoflatten=True):
    "Basically just writes a raw list of dictionaries as a csv"
    if autoflatten:
        oldlines = lines
        lines = []
        for line in oldlines:
            new_line = {}
            for key, value in line.items():
                if typecheck.is_list(value):
                    for i in range(len(value)):
                        new_line[f"{key}_{i+1}"] = value[i]
                else:
                    new_line[key] = value
            lines.append(new_line)

    basepath = path.join(path.dirname(__file__), '../../../artifacts/')
    os.makedirs(basepath, exist_ok=True)
    save_csv(lines, path.join(basepath, filename))