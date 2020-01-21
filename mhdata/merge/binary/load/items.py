from typing import Iterable
from mhw_armor_edit.ftypes import itm

from .bcore import load_schema, load_text

item_dupes = [
    "Coral Crystal"
]

def rarity_to_rank(rarity):
    if rarity >= 9:
        return 'MR'
    if rarity >= 5:
        return 'HR'
    return 'LR'

class ItemUpdater:
    def __init__(self):
        self.item_text = load_text("common/text/steam/item")
        self.item_data = sorted(
            load_schema(itm.Itm, "common/item/itemData.itm").entries,
            key=lambda i: i.order)

        self.item_data_map = {i.id:i for i in self.item_data}

        self.encountered_item_ids = set()
        
    def add_missing_items(self, encountered_item_ids: Iterable[int]):
        self.encountered_item_ids.update(encountered_item_ids)

    def _resolve_name(self, binary_item_id):
        name = self.item_text[binary_item_id * 2]
        if name['en'] in item_dupes:
            item = self.item_data_map[binary_item_id]
            name['en'] = f"{name['en']} ({rarity_to_rank(item.rarity+1)})"
        return name

    def name_and_description_for(self, binary_item_id, track=True):
        if track: self.encountered_item_ids.add(binary_item_id)
        return (self._resolve_name(binary_item_id), self.item_text[binary_item_id * 2 + 1])

    def name_for(self, binary_item_id):
        self.encountered_item_ids.add(binary_item_id)
        return self._resolve_name(binary_item_id)