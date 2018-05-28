import os.path
from os.path import abspath, join, dirname
from types import SimpleNamespace


from mhdata.io import DataMap, DataReader, DataStitcher

# NOTE: Python doesn't seem to have a way to import siblings under a name
# Absolute import fails if you are importing via nested package
# If there is a way to access as cfg.* and schema.* I'm all ears.
from .cfg import *
from .schema import *

reader = DataReader(
    required_languages=required_languages,
    languages=list(supported_languages), 
    data_path=join(dirname(abspath(__file__)), '../../source_data')
)

def transform_dmap(dmap: DataMap, obj_schema):
    """Returns a new datamap, 
    where the items in the original have run through the marshmallow schema."""
    results = DataMap()
    for entry_id, entry in dmap.items():
        data = entry.to_dict()
        (converted, errors) = obj_schema.load(data, many=False) # converted

        if errors:
            raise Exception(str(errors))

        results.add_entry(entry_id, converted)
    return results

def load_data():
    result = SimpleNamespace()

    item_map = reader.load_base_csv("items/item_base.csv", groups=['description'])
    result.item_map = transform_dmap(item_map, ItemSchema())

    location_map = (DataStitcher(reader, dir="locations/")
                    .base_csv('location_base.csv')
                    .add_csv("location_items.csv", key="items")
                    .get())
    result.location_map = transform_dmap(location_map, LocationSchema())

    result.skill_map = reader.load_base_json("skills/skill_base.json")
    result.charm_map = reader.load_base_json('charms/charm_base.json')

    result.monster_reward_conditions_map = reader.load_base_csv("monsters/reward_conditions_base.csv")

    result.monster_map = (DataStitcher(reader, dir="monsters/")
                    .base_csv("monster_base.csv", groups=['description'])
                    .add_json("monster_weaknesses.json", key="weaknesses")
                    .add_csv("monster_hitzones.csv", key="hitzones", groups=["hitzone"])
                    .add_csv("monster_breaks.csv", key="breaks", groups=["part"])
                    .add_json("monster_habitats.json", key="habitats")
                    .add_csv("monster_rewards.csv", key="rewards")
                    .get())

    armor_map = (DataStitcher(reader, dir="armors/")
                    .base_csv("armor_base.csv")
                    .add_json("armor_ext.json")
                    .get())
    result.armor_map = transform_dmap(armor_map, ArmorSchema())

    result.armorset_map = transform_dmap(
        reader.load_base_csv("armors/armorset_base.csv"),
        ArmorSetSchema()
    )

    armorset_bonus_map = (DataStitcher(reader, dir="armors/")
                    .base_csv("armorset_bonus_base.csv")
                    .add_csv("armorset_bonus_skills.csv", key="skills")
                    .get())
    result.armorset_bonus_map = transform_dmap(armorset_bonus_map, ArmorSetBonus())

    # todo: stitch
    result.weapon_map = reader.load_base_json("weapons/weapon_base.json")
    result.weapon_data = reader.load_split_data_map(result.weapon_map, "weapons/weapon_data")

    result.decoration_map = (DataStitcher(reader, dir="decorations/")
                    .base_json("decoration_base.json")
                    .add_json("decoration_chances.json", key="chances")
                    .get())

    return result