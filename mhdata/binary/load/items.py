from typing import Iterable
from mhw_armor_edit.ftypes import itm

from .bcore import load_schema, load_text

item_dupes = [
    "Coral Crystal"
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
        self.items = [
            Item(i, self._resolve_name(i), self.item_text[i.id * 2 + 1])
            for i in sorted(
                load_schema(itm.Itm, "common/item/itemData.itm").entries,
                key=lambda i: i.order)]

        self.item_data_map = {i.id : i for i in self.items}

    def _resolve_name(self, item: itm.Itm):
        name = self.item_text[item.id * 2]
        if name['en'] in item_dupes:
            name['en'] = f"{name['en']} ({rarity_to_rank(item.rarity+1)})"
        return name

    def by_id(self, binary_item_id) -> Item:
        return self.item_data_map[binary_item_id]

class ItemUpdater:
    def __init__(self):
        self.data = ItemCollection()
        self.encountered_item_ids = set()
        
    def add_missing_items(self, encountered_item_ids: Iterable[int]):
        self.encountered_item_ids.update(encountered_item_ids)

    def name_and_description_for(self, binary_item_id, track=True):
        if track: self.encountered_item_ids.add(binary_item_id)
        item = self.data.by_id(binary_item_id)
        return (item.name, item.description)

    def name_for(self, binary_item_id):
        self.encountered_item_ids.add(binary_item_id)
        return self.data.by_id(binary_item_id).name

    @property
    def item_data(self) -> Iterable[Item]:
        return self.data.items