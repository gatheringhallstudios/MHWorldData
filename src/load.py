import os
import json
import re
from src.translatemap import TranslateMap

supported_languages = ['en']

def set_languages(languages):
    global supported_languages
    supported_languages = languages

def load_translate_map(data_file, validate=True):
    "Loads a translation map object using a _names.json file"
    languages_with_errors = set()

    map = TranslateMap()
    data = json.load(open(data_file, encoding="utf-8"))
    id = 1
    for row in data:
        for lang in supported_languages:
            value = row['name_' + lang]
            if not value:
                languages_with_errors.add(lang)
            else:
                map.add_entry(id, lang, value)
        id += 1

    if validate and languages_with_errors:
        raise Exception("ERROR: Missing language entries for " +
            f"{', '.join(languages_with_errors)} While loading {data_file}")
    return map


def load_data_map(parent_map : TranslateMap, data_file, lang="en"):
    """Loads a data file, using a translation map to anchor it to id
    The result is a dictionary of id -> data row
    """
    result = {}

    name_field = f'name_{lang}'
    data = json.load(open(data_file, encoding="utf-8"))
    for row in data:
        name = row.get(name_field, None)
        if not name:
            raise Exception(f"ERROR: Data file {data_file} does not contain a {name_field} field")
        id = parent_map.id_of(lang, name)
        if not id:
            raise Exception(f"ERROR: Entry {name} in {data_file} is an invalid name")
        result[id] = row
    return result

def load_language_data_dir(parent_map : TranslateMap, data_directory):
    """Loads a directory containing sub-json for each language.
    Each entry in the sub-json must have a name_language field for that language.
    The result is a dictionary mapping id->language->data
    """
    result = {}
    for dir_entry in os.scandir(data_directory):
        if not dir_entry.is_file():
            continue
        match = re.search(r'_([a-zA-Z]+)\.json$', dir_entry.name.lower())
        if not match:
            continue
        language = match.group(1).lower()
        if language not in supported_languages:
            continue

        # If we want a validation phase, then we'll need to split this function
        # if that happens, I suggest a load_language_data_raw, a validate_raw_language_data, and then this function to use the others
        # We also need to make sure that every single row has a result....we'll do that later using the translatemap.names_of function.

        name_field = f'name_{language}'
        data = json.load(open(dir_entry))
        for row in data:
            name = row.get(name_field, None)
            if not name:
                # todo: should we change language files to be keyed by the name to avoid this possibility, or the possibility of duplicates?
                raise Exception(f"ERROR: An entry in {dir_entry.name} does not have a {name_field}")

            id_value = parent_map.id_of(language, name)
            if not id_value:
                raise Exception(f"ERROR: Entry {name} in {dir_entry.name} is an invalid name")

            result[id_value] = result.get(id_value, {})
            result[id_value][language] = row

    return result
