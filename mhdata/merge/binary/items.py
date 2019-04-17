from typing import Iterable

from mhdata.io import create_writer, DataMap
from mhdata.load import load_data, schema
from mhdata.util import OrderedSet

from mhw_armor_edit.ftypes import itm

from . import artifacts
from .load import load_schema, load_text, ItemTextHandler

# Index based item type
item_type_list = [
    'item', # Consumable / Trade
    'material', # Monster Material
    'endemic', # Endemic Life
    'ammo',
    'jewel'
]

class ItemUpdater:
    def __init__(self):
        self.encountered_item_ids = set()
        
    def add_missing_items(self, encountered_item_ids: Iterable[int]):
        self.encountered_item_ids.update(encountered_item_ids)
        
    def update_items(self, *, mhdata=None):
        if not mhdata:
            mhdata = load_data()
            print("Existing Data loaded. Using to expand item list")

        item_data = sorted(
            load_schema(itm.Itm, "common/item/itemData.itm").entries,
            key=lambda i: i.order)
        item_text_manager = ItemTextHandler()

        new_item_map = DataMap(languages='en', start_id=mhdata.item_map.max_id+1)
        unlinked_item_names = OrderedSet()

        # First pass. Iterate over existing ingame items and merge with existing data
        for entry in item_data:
            name_dict, description_dict = item_text_manager.text_for(entry.id)
            existing_item = mhdata.item_map.entry_of('en', name_dict['en'])

            is_encountered = entry.id in self.encountered_item_ids
            if not is_encountered and not existing_item:
                unlinked_item_names.add(name_dict['en'])
                continue

            # note: we omit buy price as items may have a buy price even if not sold.
            # We only care about the buy price of BUYABLE items
            new_data = {
                'name': name_dict,
                'description': description_dict,
                'rarity': entry.rarity + 1,
                'sell_price': None,
                'points': None
            }

            is_ez = (entry.flags & itm.ItmFlag.IsQuestOnly.value) != 0
            is_account = item_type_list[entry.type] == 'endemic'
            is_tradein = "(Trade-in Item)" in description_dict['en']
            is_appraisal = (entry.flags & itm.ItmFlag.IsAppraisal.value) != 0

            sell_value = entry.sell_price if entry.sell_price != 0 else None
            if is_account:
                new_data['points'] = sell_value
            else:
                new_data['sell_price'] = sell_value
            
            if name_dict['en'] == 'Normal Ammo 1':
                new_data['category'] = 'hidden'
            elif is_ez:
                new_data['category'] = 'misc'
                new_data['subcategory'] = 'trade' if is_tradein else 'supply'
            elif is_account:
                new_data['category'] = 'misc'
                new_data['subcategory'] = 'trade' if is_tradein else 'account'
            elif is_appraisal or ('Appraised after investigation' in description_dict['en']):
                new_data['category'] = 'misc'
                new_data['subcategory'] = 'appraisal'
                new_data['sell_price'] = None  # why does this have values?
            else:
                new_data['category'] = item_type_list[entry.type]
                new_data['subcategory'] = 'trade' if is_tradein else None

                # Whether we show carry limit at all is based on item type.
                # Materials are basically infinite carry
                infinite_carry = new_data['category'] == 'material'
                new_data['carry_limit'] = None if infinite_carry else entry.carry_limit

            if existing_item:
                new_item_map.insert({ **existing_item, **new_data })
            else:
                new_item_map.insert(new_data)

        # Second pass, add old entries that are not in the new one
        for old_entry in mhdata.item_map.values():
            if old_entry.name('en') not in new_item_map.names('en'):
                new_item_map.insert(old_entry)


        # Third pass. Items need to be reordered based on type

        unsorted_item_map = new_item_map # store reference to former map
        def filter_category(category, subcategory=None):
            "helper that returns items and then removes from unsorted item map"
            results = []
            for item in unsorted_item_map.values():
                if item['category'] == category and item['subcategory'] == subcategory:
                    results.append(item)
            for result in results:
                del unsorted_item_map[result.id]
            return results

        normal_ammo_1 = unsorted_item_map.entry_of("en", "Normal Ammo 1")

        # start the before-mentioned third pass by creating a new map based off the old one
        new_item_map = DataMap(languages="en")
        new_item_map.extend(filter_category('item'))
        new_item_map.extend(filter_category('material'))
        new_item_map.extend(filter_category('material', 'trade'))
        if normal_ammo_1:
            new_item_map.insert(normal_ammo_1)
        new_item_map.extend(filter_category('ammo'))
        new_item_map.extend(filter_category('misc', 'appraisal'))
        new_item_map.extend(filter_category('misc', 'account'))
        new_item_map.extend(filter_category('misc', 'supply'))

        # Write out data
        writer = create_writer()

        writer.save_base_map_csv(
            "items/item_base.csv",
            new_item_map,
            schema=schema.ItemSchema(),
            translation_filename="items/item_base_translations.csv",
            translation_extra=['description']
        )

        # Write out artifact data
        print("Writing unlinked item names to artifacts")
        artifacts.write_names_artifact('items_unlinked.txt', unlinked_item_names)

        print("Item files updated")
