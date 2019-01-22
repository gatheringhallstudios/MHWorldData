from typing import Type, Mapping, Iterable
from os.path import dirname, abspath, join
import re

from mhdata import cfg
from mhdata.util import OrderedSet, Sharpness

from mhw_armor_edit import ftypes
from mhw_armor_edit.ftypes import gmd, kire, wp_dat, wp_dat_g, eq_crt, eq_cus

# Location of MHW binary data.
# Looks for a folder called /mergedchunks neighboring the main project folder.
# This folder should be created via WorldChunkTool, with each numbered chunk being
# moved into the mergedchunks folder in ascending order (with overwrite).
CHUNK_DIRECTORY = join(dirname(abspath(__file__)), "../../../../mergedchunks")

# Mapping from GMD filename suffix to actual language code
lang_map = {
    'eng': 'en',
    'jpn': 'ja',
    'fre': 'fr',
    'ger': 'de',
    'ita': 'it',
    'spa': 'es',
    'ptB': 'pt',
    'pol': 'pl',
    'rus': 'ru',
    'kor': 'ko',
    'chT': 'zh',
    'ara': 'ar',
}

def load_schema(schema: Type[ftypes.StructFile], relative_dir: str) -> ftypes.StructFile:
    "Uses an ftypes struct file class to load() a file relative to the chunk directory"
    with open(join(CHUNK_DIRECTORY, relative_dir), 'rb') as f:
        return schema.load(f)

def load_text(basepath: str) -> Mapping[int, Mapping[str, str]]:
    """Parses a series of GMD files, returning a mapping from index -> language -> value
    
    The given base path is the relative directory from the chunk folder,
    excluding the _eng.gmd ending. All GMD files starting with the given basepath
    and ending with the language are combined together into a single result.
    """
    results = {}
    for ext_lang, lang in lang_map.items():
        data = load_schema(gmd.Gmd, f"{basepath}_{ext_lang}.gmd")
        for idx, value_obj in enumerate(data.items):
            if idx not in results:
                results[idx] = {}
            value = value_obj.value
            value = re.sub(r"( )*\r?\n( )*", " ", value)
            value = re.sub(r"( )?<ICON ALPHA>", " α", value)
            value = re.sub(r"( )?<ICON BETA>", " β", value)
            value = re.sub(r"( )?<ICON GAMMA>", " γ", value)
            results[idx][lang] = (value
                                    .replace("<STYL MOJI_YELLOW_DEFAULT>[1]</STYL>", "[1]")
                                    .replace("<STYL MOJI_YELLOW_DEFAULT>[2]</STYL>", "[2]")
                                    .replace("<STYL MOJI_YELLOW_DEFAULT>[3]</STYL>", "[3]")
                                    .replace("<STYL MOJI_YELLOW_DEFAULT>", "")
                                    .replace("<STYL MOJI_LIGHTBLUE_DEFAULT>", "")
                                    .replace("</STYL>", "")).strip()
    return results

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

class SharpnessDataReader():
    "A class that loads sharpness data and processes it for binary weapon objects"
    def __init__(self):
        self.sharpness_data = load_schema(kire.Kire, "common/equip/kireaji.kire")

    def sharpness_for(self, binary: wp_dat.WpDatEntry):
        """"Returns sharpness data for the given binary weapon entry.
        This sharpness data is in the form used in the sharpness csv file"""

        sharpness_binary = self.sharpness_data[binary.kire_id]
        sharpness_modifier = -250 + (binary.handicraft*50)
        sharpness_maxed = sharpness_modifier == 0
        if not sharpness_maxed:
            sharpness_modifier += 50 # we store the handicraft+5 value...

        # Binary data lists "end" positions, not pool sizes
        # So we convert by subtracting the previous end position
        sharpness_values = Sharpness(
            red=sharpness_binary.red,
            orange=sharpness_binary.orange-sharpness_binary.red,
            yellow=sharpness_binary.yellow-sharpness_binary.orange,
            green=sharpness_binary.green-sharpness_binary.yellow,
            blue=sharpness_binary.blue-sharpness_binary.green,
            white=sharpness_binary.white-sharpness_binary.blue,
            purple=sharpness_binary.purple-sharpness_binary.white)
        sharpness_values.subtract(-sharpness_modifier)

        return {
            'maxed': sharpness_maxed,
            **sharpness_values.to_object()
        }
        
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

# wp_dat files (mapping from filename -> mhwdb weapon type)
# ranged ones map to wp_dat_g instead
weapon_files = {
    cfg.GREAT_SWORD: 'l_sword',
    cfg.LONG_SWORD: 'tachi',
    cfg.SWORD_AND_SHIELD: 'sword',
    cfg.DUAL_BLADES: 'w_sword',
    cfg.HAMMER: 'hammer',
    cfg.HUNTING_HORN: 'whistle',
    cfg.LANCE: 'lance',
    cfg.GUNLANCE: 'g_lance',
    cfg.SWITCH_AXE: 's_axe',
    cfg.CHARGE_BLADE: 'c_axe',
    cfg.INSECT_GLAIVE: 'rod',
    cfg.LIGHT_BOWGUN: 'lbg',
    cfg.HEAVY_BOWGUN: 'hbg',
    cfg.BOW: 'bow'
}

# A list of weapon types ordered by ingame ordering. 
# Positioning here corresponds to equip type
weapon_types = [
    cfg.GREAT_SWORD, cfg.SWORD_AND_SHIELD, cfg.DUAL_BLADES, cfg.LONG_SWORD,
    cfg.HAMMER, cfg.HUNTING_HORN, cfg.LANCE, cfg.GUNLANCE, cfg.SWITCH_AXE,
    cfg.CHARGE_BLADE, cfg.INSECT_GLAIVE, cfg.BOW, cfg.HEAVY_BOWGUN, cfg.LIGHT_BOWGUN
]

class WeaponDataNode():
    def __init__(self, binary, wtype: str, name: dict, tree: str, craft: eq_crt.EqCrtEntry, upgrade: eq_cus.EqCusEntry):
        self.binary = binary
        self.wtype = wtype
        self.name = name
        self.tree = tree
        self.craft = craft
        self.upgrade = upgrade

        self.parent = None
        self.children = []

    @property
    def id(self):
        return self.binary.id
    
    def add_child(self, child: 'WeaponDataNode'):
        child.parent = self
        self.children.append(child)

class WeaponTree(Iterable[WeaponDataNode]):
    def __init__(self, weapon_map: Mapping[int, WeaponDataNode]):
        self.weapon_map = weapon_map

        # mini-pass (map by name)
        self.weapon_map_by_name = {}
        for weapon in self.weapon_map.values():
            self.weapon_map_by_name[weapon.name['en']] = weapon

        # Figure out which are the roots.
        # Note that insertion order is the correct order.
        self.roots = []
        for weapon in self.weapon_map.values():
            if weapon.parent == None:
                self.roots.append(weapon)

    def by_id(self, entry_id):
        return self.weapon_map[entry_id]

    def by_name(self, name_en):
        return self.weapon_map_by_name[name_en]

    def __iter__(self):
        "Depth-first search iteration of the weapon tree"
        stack = []
        stack.extend(reversed(self.roots))

        while stack:
            current_item = stack.pop()
            yield current_item
            if current_item.children:
                stack.extend(reversed(current_item.children))

class WeaponDataLoader():
    def __init__(self):
        self.weapon_trees = load_text("common/text/steam/wep_series")
        
        # Retrieve all creation data
        self.crafting_data_map = {}
        for entry in load_schema(eq_crt.EqCrt, "common/equip/weapon.eq_crt").entries:
            wtype = weapon_types[entry.equip_type]
            self.crafting_data_map[(wtype, entry.equip_id)] = entry

        # Retrieve all upgrade data. Include "invalid ones" as they contain descendant data
        # Also prioritizes later ones over earlier ones.
        self.upgrade_data = load_schema(eq_cus.EqCus, "common/equip/weapon.eq_cus")
        self.upgrade_data_map = {}
        for entry in self.upgrade_data.entries:
            wtype = weapon_types[entry.equip_type]
            self.upgrade_data_map[(wtype, entry.equip_id)] = entry

    def load_tree(self, weapon_type: str) -> WeaponTree:
        "Loads the weapon tree of a type"
        binary_weapon_type = weapon_files[weapon_type]

        weapon_text = load_text(f"common/text/steam/{binary_weapon_type}")
        if weapon_type in cfg.weapon_types_melee:
            weapon_binaries = load_schema(wp_dat.WpDat, f"common/equip/{binary_weapon_type}.wp_dat")
        else:
            weapon_binaries = load_schema(wp_dat_g.WpDatG, f"common/equip/{binary_weapon_type}.wp_dat_g")
        
        # First pass - create weapon map (id -> WeaponDataNode objects)
        weapon_map = {}
        weapon_descendants = {}
        for binary in weapon_binaries.entries:
            name = weapon_text[binary.gmd_name_index]
            recipe_key = (weapon_type, binary.id)
            craft_recipe = self.crafting_data_map.get(recipe_key)
            upgrade_recipe = self.upgrade_data_map.get(recipe_key)

            # Remove craft recipe if invalid
            if craft_recipe and craft_recipe.item1_qty == 0:
                craft_recipe = None

            # Pull descendants from upgrade recipe
            # and then clear if there are no ingredients
            if upgrade_recipe:
                weapon_descendants[binary.id] = (
                    upgrade_recipe.descendant1_idx,
                    upgrade_recipe.descendant2_idx,
                    upgrade_recipe.descendant3_idx,
                    upgrade_recipe.descendant4_idx
                )

                if upgrade_recipe.item1_qty == 0:
                    upgrade_recipe = None
            
            # Skip if invalid (has no name/recipe)
            if not name['en']:
                continue
            if not craft_recipe and not upgrade_recipe:
                continue

            weapon_map[binary.id] = WeaponDataNode(
                binary,
                wtype=weapon_type,
                name=name,
                tree=self.weapon_trees[binary.tree_id]['en'],
                craft=craft_recipe, 
                upgrade=upgrade_recipe)

        # Second pass - start connecting parents and descendants
        # Iterate on upgrade recipe as that contains the descendant data
        for weapon in weapon_map.values():
            descendants = weapon_descendants.get(weapon.id, [])
            if not any(descendants):
                continue # all are 0, no descendants

            # if the first entry is 0, that means that this is the last upgrade on the tree line.
            is_last = descendants[0] == 0
            for descendant_idx in descendants:
                if descendant_idx == 0:
                    continue

                descendant_id = self.upgrade_data[descendant_idx].equip_id
                descendant = weapon_map[descendant_id]
                weapon.add_child(descendant)

            # override tree name for first descendants
            # There are no splits before final upgrade in the game UI
            if not is_last:
                weapon.children[0].tree = weapon.tree

        # Return result - the construction does some processing as well
        return WeaponTree(weapon_map)
        