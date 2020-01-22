"""
Module that handles loading, cross referencing, and finessing data. 
Used by the parent module to handle common routines or to encapsulate
harder loading procedures.
"""

from typing import Type, Mapping, Iterable

# What we're exporting
from .bcore import get_chunk_root, load_schema, load_text
from .equipment_bload import SharpnessDataReader, WeaponDataLoader, load_kinsect_tree, load_armor_series
from .quest_bload import load_quests
from .skill import SkillTextHandler
from .items import ItemUpdater

def convert_recipe(item_handler: ItemUpdater, recipe_binary) -> dict:
    "Converts a recipe binary (of type eq_cus/eq_crt) to a dictionary"
    new_data = {}
    
    for i in range(1, 4+1):
        item_id = getattr(recipe_binary, f'item{i}_id')
        item_qty = getattr(recipe_binary, f'item{i}_qty')

        item_name = None if item_qty == 0 else item_handler.name_for(item_id)['en']
        new_data[f'item{i}_name'] = item_name
        new_data[f'item{i}_qty'] = item_qty if item_qty else None

    return new_data