from mhdata.io import create_writer, DataMap
from mhdata.load import schema
from mhdata.binary.load import SkillTextHandler, ItemCollection

def translate_skills(mhdata):
    print("Translating skills")

    skilltext = SkillTextHandler()
    for skill in mhdata.skill_map.values():
        skill_name = skill['name']['en']
        try:
            (new_name, new_description) = skilltext.get_skilltree_translation(skill_name)
            skill['name'] = new_name
            skill['description'] = new_description
        except KeyError:
            print(f"Could not find skill {skill_name} in the game files")
            continue

        for level in skill['levels']:
            current_description = level['description']['en']
            try:
                description = skilltext.get_skill_description_translation(current_description)
                level['description'] = description
            except KeyError:
                print(f"Failed to find description translations for skill {skill_name} level {level['level']}")

    writer = create_writer()

    writer.save_base_map_csv(
        "skills/skill_base.csv",
        mhdata.skill_map,
        schema=schema.SkillBaseSchema(),
        translation_filename="skills/skill_base_translations.csv",
        translation_extra=['description']
    )

    writer.save_data_csv(
        "skills/skill_levels.csv",
        mhdata.skill_map,
        key='levels',
        schema=schema.SkillLevelSchema()
    )

    print("Skill files updated\n")

def translate_decorations(mhdata, item_data: ItemCollection):
    print("Translating decorations")

    jewels = filter(lambda i: i.type == "jewel", item_data.items)
    jewel_map = { j.name['en']:j for j in jewels}

    for entry in mhdata.decoration_map.values():
        deco_name = entry['name_en']
        try:
            item = jewel_map[deco_name]
        except KeyError:
            print(f"Could not find decoration {deco_name} in the game files")
            continue
        entry['name'] = item.name

    writer = create_writer()

    writer.save_base_map_csv(
        "decorations/decoration_base.csv",
        mhdata.decoration_map,
        schema=schema.DecorationBaseSchema(),
        translation_filename="decorations/decoration_base_translations.csv"
    )
    

    print("Decoration files updated\n")