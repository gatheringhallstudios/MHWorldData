import os.path
from src.data import DataReader

supported_ranks = ['lr', 'hr']
supported_languages = ['en']

this_dir = os.path.dirname(os.path.abspath(__file__))
reader = DataReader(languages=supported_languages, data_path=this_dir)

location_map = reader.load_base_map('locations/location_base.json')
item_map = reader.load_base_map("items/item_base.json")
skill_map = reader.load_base_map("skills/skill_base.json")
charm_map = reader.load_base_map('charms/charm_base.json')

monster_map = (reader.start_load("monsters/monster_base.json")
                .add_data("monsters/monster_data.json")
                .add_data("monsters/monster_rewards.json")
                .add_data("monsters/monster_habitats.json", key="habitats")
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
