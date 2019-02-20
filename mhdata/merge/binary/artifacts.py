import os
from os import path

def write_artifact(filename, raw_data: str):
    """Writes an artifact file, 
    which is a temporary fakefile used to gauge game data
    """
    basepath = path.join(path.dirname(__file__), '../../../artifacts/')

    os.makedirs(basepath, exist_ok=True)
    with open(path.join(basepath, filename), 'w', encoding='utf8') as f:
        f.write(raw_data)

def write_names_artifact(filename, names: str):
    write_artifact(filename, '\n'.join(names))
