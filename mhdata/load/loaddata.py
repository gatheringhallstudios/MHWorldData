import os.path
from os.path import abspath, join, dirname
from types import SimpleNamespace

from mhdata import cfg
from mhdata.io import DataMap, DataReader, DataStitcher, create_reader
from mhdata.io.csv import read_csv

from . import schema

reader = create_reader()

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
    """Loads all data from the source_data/ directory
    
    All data is merged together using data stitchers and run through a schema.
    The schemas perform additional type transformations, column merging into dicts (groups),
    and minor validations.
    """
    result = SimpleNamespace()

    result.item_map = (DataStitcher(reader, dir="items")
                    .base_csv("item_base.csv")
                    .extend_base("item_base_translations.csv")
                    .get(schema=schema.ItemSchema()))

    result.item_combinations = reader.load_list_csv(
        'items/item_combination_list.csv',
        schema=schema.ItemCombinationSchema())

    result.location_map = (DataStitcher(reader, dir="locations/")
                    .base_csv('location_base.csv')
                    .add_csv("location_items.csv", key="items")
                    .add_csv("location_camps.csv", key="camps")
                    .get(schema=schema.LocationSchema()))

    result.skill_map = (DataStitcher(reader, dir="skills/")
                    .base_csv("skill_base.csv")
                    .add_csv("skill_levels.csv", key="levels")
                    .get(schema=schema.SkillSchema()))

    result.charm_map = (DataStitcher(reader, dir="charms/")
                    .base_csv("charm_base.csv")
                    .extend_base('charm_base_translations.csv')
                    .add_json("charm_ext.json")
                    .get(schema=schema.CharmSchema()))

    result.monster_reward_conditions_map = reader.load_base_csv("monsters/reward_conditions_base.csv")

    result.monster_map = (DataStitcher(reader, dir="monsters/")
                    .base_csv("monster_base.csv")
                    .extend_base("monster_base_translations.csv")
                    .add_json("monster_weaknesses.json", key="weaknesses")
                    .add_csv("monster_hitzones.csv", key="hitzones", groups=["hitzone"])
                    .add_csv("monster_breaks.csv", key="breaks", groups=["part"])
                    .add_csv_ext("monster_ailments.csv", key="ailments")
                    .add_csv("monster_habitats.csv", key="habitats")
                    .add_csv("monster_rewards.csv", key="rewards")
                    .get(schema=schema.MonsterSchema()))

    result.armor_map = (DataStitcher(reader, dir="armors/")
                    .base_csv("armor_base.csv")
                    .extend_base("armor_base_translations.csv")
                    .add_csv_ext("armor_craft_ext.csv", key="craft")
                    .add_csv_ext("armor_skills_ext.csv", key="skills")
                    .get(schema=schema.ArmorSchema()))

    result.armorset_map = (DataStitcher(reader, dir="armors/")
                    .base_csv("armorset_base.csv")
                    .extend_base("armorset_base_translations.csv")
                    .get(schema=schema.ArmorSetSchema()))

    result.armorset_bonus_map = (DataStitcher(reader, dir="armors/")
                    .base_csv("armorset_bonus_base.csv")
                    .extend_base("armorset_bonus_base_translations.csv")
                    .get(schema=schema.ArmorSetBonus()))

    # Load Ammo config.
    result.weapon_ammo_map = reader.load_keymap_csv("weapons/weapon_ammo.csv", schema.WeaponAmmoSchema())

    # Load weapon data
    result.weapon_map = (DataStitcher(reader, dir="weapons/")
                    .base_csv("weapon_base.csv")
                    .extend_base('weapon_base_translations.csv')
                    .add_csv_ext("weapon_sharpness.csv", key="sharpness")
                    .add_csv_ext("weapon_bow_ext.csv", key="bow")
                    .add_csv("weapon_craft_ext.csv", key="craft")
                    .get(schema=schema.WeaponSchema()))

    # Load decoration data
    result.decoration_map = (DataStitcher(reader, dir="decorations/")
                    .base_csv("decoration_base.csv")
                    .extend_base('decoration_base_translations.csv')
                    .add_json("decoration_chances.json", key="chances")
                    .get(schema=schema.DecorationSchema()))

    return result