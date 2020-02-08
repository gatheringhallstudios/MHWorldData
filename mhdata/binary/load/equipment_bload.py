from typing import Type, Mapping, Iterable

from mhw_armor_edit.ftypes import gmd, am_dat, kire, wp_dat, wp_dat_g, eq_crt, eq_cus
from mhw_armor_edit.ftypes.ext import rod_inse

from mhdata import cfg
from mhdata.util import Sharpness

from .bcore import load_schema, load_text

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

def iter_recipe(recipe):
    if recipe:
        for i in range(1, 4+1):
            item_id = getattr(recipe, f'item{i}_id')
            item_qty = getattr(recipe, f'item{i}_qty')
            if item_qty == 0:
                continue
            yield (item_id, item_qty)

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


class EquipmentNode():
    "A tree node that holds onto a weapon. Useful for weapon trees"
    def __init__(self, binary, wtype: str, name: dict, tree: str, craft: eq_crt.EqCrtEntry, upgrade: eq_cus.EqCusEntry):
        self.binary = binary
        self.wtype = wtype
        self.name = name
        self.tree = tree
        self.craft = list(iter_recipe(craft))
        self.upgrade = list(iter_recipe(upgrade))

        self.parent = None
        self.children = []

    @property
    def id(self):
        return self.binary.id
    
    def add_child(self, child: 'EquipmentNode'):
        child.parent = self
        self.children.append(child)

class EquipmentTree():
    def __init__(self, weapon_map: Mapping[int, EquipmentNode]):
        self.weapon_map = weapon_map

        # mini-pass (map by name)
        self.weapon_map_by_name = {}
        for weapon in self.weapon_map.values():
            self.weapon_map_by_name[weapon.name['en']] = weapon

        # Figure out which are the roots.
        # Note that insertion order is the correct order.
        self.roots = []
        self._isolated = []
        for weapon in self.weapon_map.values():
            if weapon.parent != None:
                continue
            
            if weapon.tree == None:
                self._isolated.append(weapon)
            else:
                self.roots.append(weapon)

    def by_id(self, entry_id):
        return self.weapon_map[entry_id]

    def by_name(self, name_en):
        return self.weapon_map_by_name.get(name_en)

    def crafted(self) -> Iterable[EquipmentNode]:
        "Depth-first search iteration of the weapon tree"
        stack = []
        stack.extend(reversed(self.roots))

        while stack:
            current_item = stack.pop()
            yield current_item
            if current_item.children:
                stack.extend(reversed(current_item.children))

    def isolated(self) -> Iterable[EquipmentNode]:
        "Iteration of the isolated weapons"
        for weapon in self._isolated:
            yield weapon

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

    def load_tree(self, weapon_type: str) -> EquipmentTree:
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
            
            # Skip if invalid (has no name. Kulve weapons have no recipe)
            if not name['en'] or name['en'] == 'Invalid Message':
                continue

            treename = None
            if binary.tree_id != 0:
                treename = self.weapon_trees[binary.tree_id]['en']

            weapon_map[binary.id] = EquipmentNode(
                binary,
                wtype=weapon_type,
                name=name,
                tree=treename,
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
        return EquipmentTree(weapon_map)

def load_kinsect_tree():
    kinsect_trees = load_text("common/text/steam/insect_series")
    kinsect_text = load_text(f"common/text/vfont/rod_insect")
    kinsect_binaries = load_schema(rod_inse.RodInse, 'common/equip/rod_insect.rod_inse')

    # Load upgrade data entries. These are referenced later when assembling the tree
    upgrade_data_map = {}
    upgrade_data = load_schema(eq_cus.EqCus, "common/equip/insect.eq_cus")
    for entry in upgrade_data.entries:
        wtype = weapon_types[entry.equip_type]
        upgrade_data_map[entry.equip_id] = entry

    kinsect_map = {}
    kinsect_descendants = {}
    for binary in kinsect_binaries.entries:
        name = kinsect_text[binary.id]
        upgrade_recipe = upgrade_data_map.get(binary.id)

        # Pull descendants from upgrade recipe
        # but clear if there are no ingredients
        if upgrade_recipe:
            kinsect_descendants[binary.id] = (
                upgrade_recipe.descendant1_idx,
                upgrade_recipe.descendant2_idx,
                upgrade_recipe.descendant3_idx,
                upgrade_recipe.descendant4_idx
            )

            if upgrade_recipe.item1_qty == 0:
                upgrade_recipe = None
        
        if not name['en'] or name['en'] == 'Invalid Message':
            continue

        kinsect_map[binary.id] = EquipmentNode(
            binary,
            name=name,
            wtype=None,
            tree=kinsect_trees[binary.tree_id],
            craft=None, # kinsects are not craftable, only purchaseable
            upgrade=upgrade_recipe)

    # Second pass - start connecting parents and descendants
    # Iterate on upgrade recipe as that contains the descendant data
    for kinsect in kinsect_map.values():
        descendants = kinsect_descendants.get(kinsect.id, [])
        if not any(descendants):
            continue # all are 0, no descendants

        # if the first entry is 0, that means that this is the last upgrade on the tree line.
        is_last = descendants[0] == 0
        for descendant_idx in descendants:
            if descendant_idx == 0:
                continue

            descendant_id = upgrade_data[descendant_idx].equip_id
            descendant = kinsect_map[descendant_id]
            kinsect.add_child(descendant)

        # override tree name for first descendants
        # There are no splits before final upgrade in the game UI
        if not is_last:
            kinsect.children[0].tree = kinsect.tree

    # Return result - the construction does some processing as well
    return EquipmentTree(kinsect_map)

class ArmorData:
    def __init__(self, binary: am_dat.AmDatEntry, name, recipe):
        self.binary = binary
        self.name = name
        self.recipe = list(iter_recipe(recipe))

    @property
    def order(self):
        return self.binary.order

    @property
    def part(self):
        "Returns the armor part that this armor is part of"
        return [
            'head', 'chest', 'arms', 'waist', 'legs', 'charm'
        ][self.binary.equip_slot]

    @property
    def rarity(self):
        "Rarity of the armor (1 indexed)"
        return self.binary.rarity + 1

    @property
    def rank(self):
        if self.binary.variant == 0:
            return 'LR'
        elif self.rarity < 9:
            return 'HR'
        else:
            return 'MR'

class ArmorSetData:
    def __init__(self, name, armors: Iterable[ArmorData]):
        self.name = name
        self.armors = armors
        self.order = min(self.armors, key=lambda a:a.order).order

        self._armor_by_part = { a.part:a for a in self.armors }
    
    def get_part(self, partname):
        return self._armor_by_part.get(partname, None)

    @property
    def rank(self):
        return self.armors[0].rank

    @property
    def rank_order(self):
        if self.rank == 'LR':
            return 0
        else:
            return 1
        
def load_armor_series():
    # Loaded armor text and armor series information
    armor_text = load_text("common/text/steam/armor")
    armorset_text = load_text("common/text/steam/armor_series")

    # Parses craft data, mapped by the binary armor id
    armor_craft_data = {}
    for craft_entry in load_schema(eq_crt.EqCrt, "common/equip/armor.eq_crt").entries:
        armor_craft_data[craft_entry.equip_id] = craft_entry

    # Parses binary armor data.
    armor_by_setid = {}
    for armor_binary in load_schema(am_dat.AmDat, "common/equip/armor.am_dat").entries:
        name_dict = armor_text[armor_binary.gmd_name_index]
        
        if not name_dict or not name_dict['en']: continue
        if armor_binary.set_id == 0: continue # skip charms (for now)
        if armor_binary.type != 0: continue # type 0 is regular armor
        if armor_binary.gender == 0: continue
        if armor_binary.order == 0: continue
        
        craft_recipe = armor_craft_data.get(armor_binary.id, None)
        if not craft_recipe:
            continue

        armor_data = ArmorData(
            binary=armor_binary,
            name=name_dict,
            recipe=craft_recipe
        )

        set_id = armor_binary.set_id
        armor_by_setid.setdefault(set_id, [])
        armor_by_setid[set_id].append(armor_data)

    # Assemble armor series
    armor_sets = []
    for set_id, armors in armor_by_setid.items():
        series_name_dict = armorset_text[set_id]
        
        set_data = ArmorSetData(
            name=series_name_dict,
            armors=armors
        )

        armor_sets.append(set_data)

    armor_sets.sort(key=lambda a: (a.rank_order, a.order))

    return { aset.name['en']:aset for aset in armor_sets }

