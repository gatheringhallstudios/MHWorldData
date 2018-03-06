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

    if languages_with_errors:
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
        

monster_map = load_translate_map("monsters/monster_names.json")
skill_map = load_translate_map("skills/skill_names.json")
item_map = load_translate_map("items/item_names.json")
armor_map = load_translate_map("armors/armor_names.json")
armorset_map = load_translate_map("armors/armor_set_names.json")

def build_monsters(session : sqlalchemy.orm.Session):
    # Load additional files
    description = load_language_data_dir(monster_map, 'monsters/monster_descriptions')

    for row in monster_map:
        monster = db.Monster(id=row.id)
        session.add(monster)

        for language in supported_languages:
            monster_text = db.MonsterText(id=row.id, lang_id=language)
            monster_text.name = row[language]
            monster_text.description = description[row.id][language][f'description_{language}']
            session.add(monster_text)
    print("Built Monsters")


def build_skills(session : sqlalchemy.orm.Session):
    skilldata = load_language_data_dir(skill_map, 'skills/skills')
    for row in skill_map:
        skilltree = db.SkillTree(id=row.id)
        session.add(skilltree)

        for language in supported_languages:
            skilldata_row = skilldata[row.id][language] 

            name = row[language]
            description = skilldata_row[f'description_{language}']

            session.add(db.SkillTreeText(
                id=row.id, lang_id=language, name=name, description=description))

            for effect in skilldata_row['effects']:
                level = effect['level']
                effect_description = effect[f'description_{language}']
                session.add(db.Skill(
                    skilltree_id=row.id,
                    lang_id=language,
                    level = level,
                    description=effect_description
                ))
    
    print("Built Skills")

def build_items(session : sqlalchemy.orm.Session):
    # Only item names exist now...so this is simple
    for row in item_map:
        item = db.Item(id=row.id)
        session.add(item)

        for language in supported_languages:
            item_text = db.ItemText(id=row.id, lang_id=language)
            item_text.name = row[language]
            session.add(item_text)
    
    print("Built Items")

def build_armor(session : sqlalchemy.orm.Session):
    # Write entries for all armor set names first
    for (id, language, name) in armorset_map.all_items():
        armorset = db.ArmorSet(id=id, lang_id=language, name=name)
        session.add(armorset)

    data_map = load_data_map(armor_map, 'armors/armor_data.json')
    for row in armor_map:
        armor_name_en = row['en']
        data = data_map[row.id]

        armor = db.Armor(id = row.id)
        armor.rarity = data['rarity']
        armor.armor_type = data['armor_type']
        armor.male = data['male']
        armor.female = data['female']
        armor.slot_1 = data['slots'][0]
        armor.slot_2 = data['slots'][1]
        armor.slot_3 = data['slots'][2]
        armor.defense = data['defense']
        armor.fire = data['fire']
        armor.water = data['water']
        armor.thunder = data['thunder']
        armor.ice = data['ice']
        armor.dragon = data['dragon']

        armorset_id = armorset_map.id_of("en", data['set'])
        if not armorset_id:
            raise Exception(f"ERROR: Armorset {data['set']} in Armor {armor_name_en} does not exist")
        armor.armorset_id = armorset_id

        session.add(armor)

        for language in supported_languages:
            armor_text = db.ArmorText(id=row.id, lang_id=language)
            armor_text.name = row[language]
            session.add(armor_text)

        # Armor Skills
        for skill, level in data['skills'].items():
            skill_id = skill_map.id_of('en', skill)
            if not skill_id:
                raise Exception(f"ERROR: Skill {skill} in Armor {armor_name_en} does not exist")
            session.add(db.ArmorSkill(
                armor_id = row.id,
                skill_id = skill_id,
                level = level
            ))
        
        # Armor Crafting
        for item, quantity in data['craft'].items():
            item_id = item_map.id_of('en', item)
            if not item_id:
                raise Exception(f"ERROR: Item {item} in Armor {armor_name_en} does not exist")
            session.add(db.ArmorRecipe(
                armor_id = row.id,
                item_id = item_id,
                quantity = quantity
            ))

    print("Built Armor")


sessionbuilder = db.recreate_database(output_filename)

with db.session_scope(sessionbuilder) as session:
    build_monsters(session)
    build_skills(session)
    build_items(session)
    build_armor(session)
    print("Finished build")
