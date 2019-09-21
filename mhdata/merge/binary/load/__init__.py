from typing import Type, Mapping, Iterable

from mhdata.util import OrderedSet, bidict
from mhw_armor_edit.ftypes import skl_pt_dat

# What we're exporting
from .bcore import load_schema, load_text, get_chunk_root
from .equipment_bload import SharpnessDataReader, WeaponDataLoader, load_kinsect_tree, load_armor_series
from .quest_bload import load_quests

class ItemTextHandler():
    "A class that loads item text and tracks encountered items"

    def __init__(self):
        self._item_text = load_text("common/text/steam/item")
        self.encountered = OrderedSet()

    def name_for(self, item_id: int):
        self.encountered.add(item_id)
        return self._item_text[item_id * 2]

    def description_for(self, item_id: int):
        self.encountered.add(item_id)
        return self._item_text[item_id * 2 + 1]

    def text_for(self, item_id: int):
        self.encountered.add(item_id)
        return (self._item_text[item_id * 2], self._item_text[item_id * 2 + 1])

def convert_recipe(item_text_handler: ItemTextHandler, recipe_binary) -> dict:
    "Converts a recipe binary (of type eq_cus/eq_crt) to a dictionary"
    new_data = {}
    
    for i in range(1, 4+1):
        item_id = getattr(recipe_binary, f'item{i}_id')
        item_qty = getattr(recipe_binary, f'item{i}_qty')

        item_name = None if item_qty == 0 else item_text_handler.name_for(item_id)['en']
        new_data[f'item{i}_name'] = item_name
        new_data[f'item{i}_qty'] = item_qty if item_qty else None

    return new_data

class SkillTextHandler():
    def __init__(self):    
        self.skilltree_text = load_text("common/text/vfont/skill_pt")
        
        # mapping from name -> skill tree entry
        self.skill_map = bidict()
        for entry in load_schema(skl_pt_dat.SklPtDat, "common/equip/skill_point_data.skl_pt_dat").entries:
            name = self.get_skilltree_name(entry.index)['en']
            self.skill_map[name] = entry

    def get_skilltree_name(self, skill_index: int) -> dict:
        # Discovered formula via inspecting mhw_armor_edit's source.
        return self.skilltree_text[skill_index * 3]

    def get_skilltree(self, name_en: str) -> skl_pt_dat.SklPtDatEntry:
        return self.skill_map[name_en]
