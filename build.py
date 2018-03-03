import os

import json
import re
import sqlalchemy.orm

from src.translatemap import TranslateMap
import src.db as db

output_filename = 'mhw.db'
supported_languages = ['en']

# todo: move somewhere
def load_translate_map(data_file):
    "Loads a translation map object using a _names.json file"
    map = TranslateMap()
    data = json.load(open(data_file, encoding="utf-8"))
    id = 1
    for row in data:
        for lang in supported_languages:
            map.add_entry(id, lang, row['name_' + lang])
        id += 1
    return map

def load_language_data(parent_map : TranslateMap, data_directory):
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
        

monster_map = load_translate_map("monsters/monster_names.json")
skills_map = load_translate_map("skills/skill_names.json")
items_map = load_translate_map("items/item_names.json")
armor_map = load_translate_map("armors/armor_names.json")

def build_monsters(session : sqlalchemy.orm.Session):
    # Load additional files
    description = load_language_data(monster_map, 'monsters/monster_descriptions')

    for row in monster_map:
        monster = db.Monster(id=row.id)
        session.add(monster)

        for language in supported_languages:
            monster_text = db.MonsterText(id=row.id, lang_id=language)
            monster_text.name = monster_map[row.id][language]
            monster_text.description = description[row.id][language][f'description_{language}']
            session.add(monster_text)


def build_skills(session : sqlalchemy.orm.Session):
    pass

def build_items(session : sqlalchemy.orm.Session):
    pass

def build_armor(session : sqlalchemy.orm.Session):
    pass

sessionbuilder = db.recreate_database(output_filename)

with db.session_scope(sessionbuilder) as session:
    build_monsters(session)
    build_skills(session)
    build_items(session)
    build_armor(session)
    print("Finished build")
