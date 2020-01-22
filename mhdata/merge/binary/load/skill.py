from typing import Tuple
from mhdata.util import OrderedSet, bidict
from .bcore import load_schema, load_text
from mhw_armor_edit.ftypes import skl_pt_dat

# Sometimes capcom makes mistakes, so we override them
skill_overrides = {
    102: 'Slinger Capacity'
}

def normalize_desc(val: str):
    val['en'] = val['en'].replace("  ", " ")
    return val

class SkillTextHandler():
    def __init__(self):    
        self.skilltree_text = load_text("common/text/vfont/skill_pt")
        self.skill_text = load_text("common/text/vfont/skill", exclude_indices=True)
        
        # mapping from name -> skill tree entry
        self.skill_map = bidict()
        for entry in load_schema(skl_pt_dat.SklPtDat, "common/equip/skill_point_data.skl_pt_dat").entries:
            name = self.get_skilltree_name(entry.index)['en']
            self.skill_map[name] = entry

        self.skill_ex = {}
        self.skill_description_ex = {}
        self.description_translations = {}
        for (index, (key, entry)) in enumerate(self.skill_text.items()):
            if key.endswith('_DESC'):
                entry = normalize_desc(entry)
                self.description_translations[entry['en']] = entry
            elif key.endswith('_SKILL') and entry != 'Invalid Message':
                key_base = key[:-6]
                self.skill_ex[entry['en']] = entry
                self.skill_description_ex[entry['en']] = self.skill_text[key + "_DESC"]

    def get_skilltree_name(self, skill_index: int) -> dict:
        # Discovered formula via inspecting mhw_armor_edit's source.
        name = self.skilltree_text[skill_index * 3]
        if skill_index in skill_overrides.keys():
            for lang, value in name.items():
                if value == "Invalid Message":
                    name[lang] = skill_overrides[skill_index]
        return name

    def get_skilltree_description(self, skill_index: int) -> dict:
        description = self.skilltree_text[(skill_index * 3) + 2]
        return description

    def get_skill_description_translation(self, description: str) -> dict:
        "Retrieves all translations for a given skill description, throws KeyError if doesn't exist"
        return self.description_translations[description]

    def get_skilltree(self, name_en: str) -> skl_pt_dat.SklPtDatEntry:
        """Retrieves the skill tree entry if exists, throws a KeyError if it does not"""
        return self.skill_map[name_en]

    def get_skilltree_translation(self, name_en: str) -> Tuple[dict, dict]:
        "Get translations for a skilltree, including pseudo skills like Good Luck"
        name = None
        description = None
        try:
            skilltree = self.get_skilltree(name_en)
            name = self.get_skilltree_name(skilltree.index)
            description = self.get_skilltree_description(skilltree.index)
        except KeyError:
            name = self.skill_ex[name_en]
            description = self.skill_description_ex[name_en]

        return (name, description)