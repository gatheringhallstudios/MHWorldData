from mhdata.util import OrderedSet, bidict
from .bcore import load_schema, load_text
from mhw_armor_edit.ftypes import skl_pt_dat

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
