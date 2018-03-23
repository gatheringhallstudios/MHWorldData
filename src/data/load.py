import os
import json
import re
from .translatemap import TranslateMap
from .datamap import DataMap
from .config import get_languages, get_data_path

class JoinResult:
    def __init__(self, obj, invalid, missing_count, join_field):
        self.obj = obj
        self.invalid_entries = invalid
        self.missing_count = missing_count
        self.join_field = join_field

def _join(parent_map, data_list : list, lang):
    """Inner function to join a parent_map to a data_obj, 
    returning a JoinResult
    """
    result = {}
    missing_fields = 0
    invalid_entries = set()
    name_field = f'name_{lang}'

    for row in data_list:
        name = row.get(name_field, None)
        if not name:
            missing_fields += 1
            continue
            
        id = parent_map.id_of(lang, name)
        if not id:
            invalid_entries.add(name)
            continue
            
        result[id] = row

    return JoinResult(result, invalid_entries, missing_fields, name_field)

def load_translate_map(data_file, validate=True):
    "Loads a translation map object using a _names.json file"
    data_file = get_data_path(data_file)
    languages_with_errors = set()

    map = TranslateMap()
    data = json.load(open(data_file, encoding="utf-8"))
    id = 1
    for row in data:
        for lang in get_languages():
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


def load_data_map(parent_map : TranslateMap, data_file, lang="en", validate=True):
    """Loads a data file, using a translation map to anchor it to id
    The result is a DataMap object mapping id -> data row
    """
    data_file = get_data_path(data_file)
    data = json.load(open(data_file, encoding="utf-8"))

    result = _join(parent_map, data, lang=lang)

    # todo: print more errors if more than one
    if validate and result.missing_count:
        raise Exception(f"ERROR: {result.missing_count} entries in " +
            f"data file {data_file} does not contain a {result.join_field} field")
    if validate and result.invalid_entries:
        raise Exception(f"ERROR: Entry {result.invalid_entries.pop()} in " +
            f"{data_file} is an invalid name")

    return DataMap(parent_map, result.obj)

def load_split_data_map(parent_map : TranslateMap, data_directory, lang="en", validate=True):
    """Loads a data map by combining separate maps in a folder into one.
    Just like a normal data map, it is anchored to the translation map.
    """
    data_directory = get_data_path(data_directory)
    results = []
    
    for dir_entry in os.scandir(data_directory):
        if not dir_entry.is_file():
            continue
        if not dir_entry.name.lower().endswith('.json'):
            continue

        subdata_json = json.load(open(dir_entry, encoding="utf-8"))
        result = _join(parent_map, subdata_json, lang=lang)

        if validate and result.missing_count:
            raise Exception(f"ERROR: {result.missing_count} entries in " +
                f"{dir_entry.name} does not contain a {result.join_field} field")
        if validate and result.invalid_entries:
            raise Exception(f"ERROR: Entry {result.invalid_entries.pop()} in " +
                f"{dir_entry.name} is an invalid name")

        results.append([dir_entry.name, result])

    final_obj = {}
    for (filename, result) in results:
        intersection = final_obj.keys() & result.obj
        # todo: identify both sources of the conflict. We only know one source
        if validate and intersection:
            raise Exception(f"ERROR: Data maps in {data_directory} have conflicting entries")

        final_obj.update(result.obj)

    return DataMap(parent_map, final_obj)

def load_language_data_dir(parent_map : TranslateMap, data_directory):
    """Loads a directory containing sub-json for each language.
    Each entry in the sub-json must have a name_language field for that language.
    The result is a dictionary mapping id->language->data
    """
    data_directory = get_data_path(data_directory)
    result = {}
    for dir_entry in os.scandir(data_directory):
        if not dir_entry.is_file():
            continue
        match = re.search(r'_([a-zA-Z]+)\.json$', dir_entry.name.lower())
        if not match:
            continue
        language = match.group(1).lower()
        if language not in get_languages():
            continue

        # If we want a validation phase, then we'll need to split this function
        # if that happens, I suggest a load_language_data_raw, a validate_raw_language_data, and then this function to use the others
        # We also need to make sure that every single row has a result....we'll do that later using the translatemap.names_of function.

        name_field = f'name_{language}'
        data = json.load(open(dir_entry, encoding='utf-8'))
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
