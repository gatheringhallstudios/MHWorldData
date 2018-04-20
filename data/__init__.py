import os.path
from src.data import DataReader

supported_ranks = ['lr', 'hr']

"A mapping of all translations"
all_languages = {
    'en': "English",
    'ja': "Japanese"
}

"A list of languages that require complete translations. Used in validation"
required_languages = ['en']

"A list of languages that can be exported"
supported_languages = ['en', 'ja']

"Languages that are designated as potential incomplete"
incomplete_languages = ['ja']

reader = DataReader(
    required_languages=required_languages,
    languages=list(supported_languages), 
    data_path=os.path.dirname(os.path.abspath(__file__))
)

location_map = reader.load_base_map('locations/location_base.json')
item_map = reader.load_base_map("items/item_base.json")
skill_map = reader.load_base_map("skills/skill_base.json")
charm_map = reader.load_base_map('charms/charm_base.json')

monster_map = (reader.start_load("monsters/monster_base.json")
                .add_data("monsters/monster_weaknesses.json", key="weaknesses")
                .add_data("monsters/monster_hitzones.json")
                .add_data("monsters/monster_breaks.json", key="breaks")
                .add_data("monsters/monster_habitats.json", key="habitats")
                .add_data("monsters/monster_rewards.json")
                .get())

armor_map = (reader.start_load("armors/armor_base.json")
                .add_data("armors/armor_data.json")
                .get())

armorset_map = reader.load_base_map("armors/armorset_base.json")

# todo: stitch
weapon_map = reader.load_base_map("weapons/weapon_base.json")
weapon_data = reader.load_split_data_map(weapon_map, "weapons/weapon_data")

decoration_map = (reader.start_load("decorations/decoration_base.json")
                    .add_data("decorations/decoration_chances.json", key="chances")
                    .get())
