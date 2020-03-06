
from typing import Type, Mapping, Iterable, Tuple
from mhw_armor_edit.ftypes import eq_crt, eq_cus
from .bcore import load_schema

def iter_recipe(recipe):
    if recipe:
        for i in range(1, 4+1):
            item_id = getattr(recipe, f'item{i}_id')
            item_qty = getattr(recipe, f'item{i}_qty')
            if item_qty == 0:
                continue
            yield (item_id, item_qty)

class CraftEntry:
    def __init__(self, index, equip_type, equip_id, items: Iterable[Tuple[int, int]]):
        self.index = index
        self.equip_type = equip_type
        self.equip_id = equip_id
        self.items = items

class CraftData:
    data: Iterable[CraftEntry]

    def __init__(self, data: eq_crt.EqCrt):
        self.data = []
        self.crafting_map = {}
        self.crafting_map_by_type = {}
        
        for rawentry in data.entries:
            etype = rawentry.equip_type
            eid = rawentry.equip_id
            entry = CraftEntry(
                index=rawentry.index,
                equip_type=rawentry.equip_type,
                equip_id=rawentry.equip_id,
                items=list(iter_recipe(rawentry))
            )

            self.crafting_map[eid] = entry
            self.crafting_map_by_type.setdefault(etype, {})[eid] = entry
            self.data.append(entry)

    def get(self, equip_id, *, type=None) -> CraftEntry:
        search_map = self.crafting_map if type is None else self.crafting_map_by_type[type]
        return search_map.get(equip_id)

    def __getitem__(self, idx) -> CraftEntry:
        return self.data[idx]

class UpgradeEntry(CraftEntry):
    items: Iterable[Tuple[int, int]]
    descendants: Iterable['UpgradeEntry']

    # True if there is a descendant in the first slot (same tree). False otherwise.
    has_direct_descendant: bool
    
    def __init__(self, binary: eq_cus.EqCusEntry, ):
        self.index = binary.index
        self.equip_type = binary.equip_type
        self.equip_id = binary.equip_id
        self.has_direct_descendant = binary.descendant1_idx != 0
        self.items = list(iter_recipe(binary))

        self.descendants = []
        self.parent = None

    def add_descendant(self, descendant_entry):
        self.descendants.append(descendant_entry)
        descendant_entry.parent = self

class UpgradeData:
    data: Iterable[UpgradeEntry]

    def __init__(self, data: eq_cus.EqCus):
        self.data = []
        self.upgrade_map = {}
        self.upgrade_map_by_type = {}

        for rawentry in data.entries:
            etype = rawentry.equip_type
            eid = rawentry.equip_id
            new_entry = UpgradeEntry(rawentry)
            self.data.append(new_entry)
            self.upgrade_map[eid] = new_entry
            self.upgrade_map_by_type.setdefault(etype, {})[eid] = new_entry

        # second pass, link up descendants
        for rawentry in data.entries:
            entry = self.data[rawentry.index]
            descendant_indices = (
                rawentry.descendant1_idx,
                rawentry.descendant2_idx,
                rawentry.descendant3_idx,
                rawentry.descendant4_idx
            )

            for descendant_idx in descendant_indices:
                if descendant_idx == 0: continue
                child_entry = self.data[descendant_idx]
                entry.add_descendant(child_entry)

    def get(self, equip_id, *, type=None) -> UpgradeEntry:
        search_map = self.upgrade_map if type is None else self.upgrade_map_by_type[type]
        return search_map.get(equip_id)

    def __getitem__(self, idx) -> UpgradeEntry:
        return self.data[idx]

def load_craft_data(filename):
    "Loads crafting data (eq_crt), using the sort of path string you'd give load_schema"
    return CraftData(load_schema(eq_crt.EqCrt, filename))

def load_upgrade_data(filename):
    "Loads upgrade data (eq_cus), using the sort of path string you'd give load schema"
    return UpgradeData(load_schema(eq_cus.EqCus, filename))