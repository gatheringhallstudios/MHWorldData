from mhdata.util import OrderedSet, bidict
from .bcore import load_schema, load_text
from mhw_armor_edit.ftypes import skl_pt_dat

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
