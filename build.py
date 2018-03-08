import sqlalchemy.orm
import src.db as db

from src.load import (
    set_languages, load_data_map, load_translate_map, load_language_data_dir
)

output_filename = 'mhw.db'
supported_languages = ['en']
set_languages(supported_languages)

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
