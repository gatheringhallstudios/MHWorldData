from typing import Iterable, Tuple
from mhw_armor_edit.ftypes import itm

from .bcore import load_schema, load_text
from mhw_armor_edit.ftypes import sgpa

item_dupes = [
    # "Coral Crystal" - later updates split into Coral Crystal and Reef Crystal
]

# items that are dummies that don't look like dummies
item_dummies = [
    2568, # green herb non-consumable
    2569, # red herb non-consumable
]

# Index based item type
item_type_list = [
    'item', # Consumable / Trade
    'material', # Monster Material
    'endemic', # Endemic Life
    'ammo',
    'jewel',
    "furniture", # ?
]

def rarity_to_rank(rarity):
    if rarity >= 9:
        return 'MR'
    if rarity >= 5:
        return 'HR'
    return 'LR'

class Item:
    def __init__(self, data: itm.ItmEntry, name, description):
        self.id = data.id
        self.data = data
        self.name = name
        self.description = description
        self.type = item_type_list[data.type]

    def __getattr__(self, name):
        # fallback to binary data
        return self.data.__getattribute__(name)

class ItemCollection:
    def __init__(self):
        self.item_text = load_text("common/text/steam/item")

        # Iterable list of all items in the game files
        self.items = [
            Item(i, self._resolve_name(i), self.item_text[i.id * 2 + 1])
            for i in sorted(
                load_schema(itm.Itm, "common/item/itemData.itm").entries,
                key=lambda i: i.order)
            if i.id not in item_dummies]

        self.item_data_map = {i.id : i for i in self.items}

    def _resolve_name(self, item: itm.Itm):
        name = self.item_text[item.id * 2]
        if name['en'] in item_dupes:
            name['en'] = f"{name['en']} ({rarity_to_rank(item.rarity+1)})"
        return name

    def by_id(self, binary_item_id) -> Item:
        return self.item_data_map[binary_item_id]

class Decoration:
    def __init__(self, item: itm.ItmEntry, size: int, skills: Iterable[Tuple[int, int]]):
        self.item = item
        self.size = size
        self.skills = skills

    @property
    def name(self):
        return self.item.name

    @property
    def rarity(self):
        return self.item.rarity + 1

    @property
    def skill1(self):
        return self.skills[0]

    @property
    def skill2(self):
        if len(self.skills) < 2:
            return None
        return self.skills[1]

class DecorationCollection:
    def __init__(self, items: ItemCollection):
        data = load_schema(sgpa.Sgpa, "common/item/skillGemParam.sgpa")
        entries = sorted(data.entries, key=lambda e: (e.size, e.order))

        def deco_from_entry(entry: sgpa.SgpaEntry):
            item = items.by_id(entry.id)
            skills = []
            for i in [1, 2]:
                skill_id = getattr(entry, f"skill{i}_id")
                skill_incr = getattr(entry, f"skill{i}_incr")
                if skill_incr > 0:
                    skills.append([skill_id, skill_incr])
            if len(skills) == 0:
                raise Exception("Unexpected no-skill entry")
            return Decoration(item, entry.size, skills)

        self.decorations = list(map(deco_from_entry, entries))
        self._decos_by_name = { d.name['en']:d for d in self.decorations }

    def by_name(self, name_en: str) -> Decoration:
        return self._decos_by_name[name_en]