# Export configuration data
from .cfg import *

# TODO: Move all of this elsewhere. 
# Its bad practice to run code at import time.

import os.path
from os.path import abspath, join, dirname

from mhwdata.io import DataReader

reader = DataReader(
    required_languages=required_languages,
    languages=list(supported_languages), 
    data_path=join(dirname(abspath(__file__)), '../../source_data')
)

location_map = reader.load_base_map('locations/location_base.json')
item_map = reader.load_base_map("items/item_base.json")
skill_map = reader.load_base_map("skills/skill_base.json")
charm_map = reader.load_base_map('charms/charm_base.json')

monster_reward_conditions_map = reader.load_base_map("monsters/reward_conditions_base.json")

monster_map = (reader.start_load("monsters/monster_base.json")
                .add_json("monsters/monster_weaknesses.json", key="weaknesses")
                .add_json("monsters/monster_hitzones.json")
                .add_json("monsters/monster_breaks.json", key="breaks")
                .add_json("monsters/monster_habitats.json", key="habitats")
                .add_json("monsters/monster_rewards.json")
                .get())

armor_map = (reader.start_load("armors/armor_base.json")
                .add_json("armors/armor_data.json")
                .get())

armorset_map = reader.load_base_map("armors/armorset_base.json")

# todo: stitch
weapon_map = reader.load_base_map("weapons/weapon_base.json")
weapon_data = reader.load_split_data_map(weapon_map, "weapons/weapon_data")

decoration_map = (reader.start_load("decorations/decoration_base.json")
                    .add_json("decorations/decoration_chances.json", key="chances")
                    .get())
