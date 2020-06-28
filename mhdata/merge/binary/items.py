from typing import Iterable

from mhdata.io import create_writer, DataMap
from mhdata.load import load_data, schema
from mhdata.util import OrderedSet
from mhw_armor_edit.ftypes import itm

from . import artifacts
from mhdata.binary import ItemCollection, Item, DecorationCollection
from mhdata.binary.load import load_schema, load_text, SkillTextHandler

class DummyItemError(Exception):
    pass

class ItemUpdater:
    def __init__(self, collection: ItemCollection):
        self.data = collection
        self.encountered_item_ids = set()

    def _check_invalid(self, item):
        if item.name['en'] in ['HARDUMMY']:
            raise DummyItemError(f"INVALID ITEM {item.name['en']}")
        
    def add_missing_items(self, encountered_item_ids: Iterable[int]):
        # Check valid (name_for does that automatically)
        [self.name_for(item_id) for item_id in encountered_item_ids]

        self.encountered_item_ids.update(encountered_item_ids)

    def name_and_description_for(self, binary_item_id, track=True):
        item = self.data.by_id(binary_item_id)
        self._check_invalid(item)
        if track: self.encountered_item_ids.add(binary_item_id)
        return (item.name, item.description)

    def name_for(self, binary_item_id):
        item = self.data.by_id(binary_item_id)
        self._check_invalid(item)
        self.encountered_item_ids.add(binary_item_id)
        return item.name

    def add_encountered_names(self, names: set):
        for name in names: 
            for item in self.data.by_name(name):
                self._check_invalid(item)
        for entry in filter(lambda d: d.name['en'] in names, self.data.items):
            self.encountered_item_ids.add(entry.id)

    @property
    def item_data(self) -> Iterable[Item]:
        return self.data.items

def register_combinations(mhdata, item_updater: ItemUpdater):
    names = set()
    for combo in mhdata.item_combinations:
        names.add(combo['result'])
        names.add(combo['first'])
        if combo['second']:
            names.add(combo['second'])
    item_updater.add_encountered_names(names)
        
def update_items(item_updater: ItemUpdater, *, mhdata=None):
    if not mhdata:
        mhdata = load_data()
        print("Existing Data loaded. Using to expand item list")

    new_item_map = DataMap(languages='en', start_id=mhdata.item_map.max_id+1)
    unlinked_item_names = OrderedSet()

    # used to track dupes to throw proper errors
    updated_names = set()

    # First pass. Iterate over existing ingame items and merge with existing data
    for entry in item_updater.item_data:
        name_dict = entry.name
        description_dict = entry.description
        existing_item = mhdata.item_map.entry_of('en', name_dict['en'])

        is_encountered = entry.id in item_updater.encountered_item_ids
        if not is_encountered and not existing_item:
            unlinked_item_names.add(name_dict['en'])
            continue

        if name_dict['en'] in updated_names:
            raise Exception(f"Duplicate item {name_dict['en']}")
        updated_names.add(name_dict['en'])

        # note: we omit buy price as items may have a buy price even if not sold.
        # We only care about the buy price of BUYABLE items
        new_data = {
            'name': name_dict,
            'description': description_dict,
            'rarity': entry.rarity + 1,
            'sell_price': None,
            'points': None
        }

        is_ez = entry.flags.ez
        is_account = entry.type == 'endemic'
        is_tradein = "(Trade-in Item)" in description_dict['en']
        is_appraisal = entry.flags.appraisal

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
            new_data['category'] = entry.type
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
    print("Writing all items and ids")
    artifact_data = [{'id': i.id, 'name': i.name['en']} for i in item_updater.data]
    artifacts.write_dicts_artifact('items_ids.csv', artifact_data)

    print("Item files updated")

def update_decorations(mhdata, item_data: ItemCollection):
    print("Updating decorations")

    data = DecorationCollection(item_data)
    skill_text_handler = SkillTextHandler()
    
    # write artifact file (used to debug)
    def create_deco_artifact(d):
        return { 'name': d.name['en'], 'slot': d.size, 'rarity': d.rarity }
    artifacts.write_dicts_artifact("decorations_all.csv",
        list(map(create_deco_artifact, data.decorations)))

    for entry in mhdata.decoration_map.values():
        deco_name = entry['name_en']
        try:
            deco = data.by_name(entry['name_en'])
        except KeyError:
            print(f"Could not find decoration {deco_name} in the game files")
            continue

        entry['name'] = deco.name
        entry['rarity'] = deco.rarity
        for i in range(2):
            skill_name = None
            skill_pts = None
            if i < len(deco.skills):
                (skill_id, skill_pts) = deco.skills[i]
                skill_name = skill_text_handler.get_skilltree_name(skill_id)['en']
            entry[f'skill{i+1}_name'] = skill_name
            entry[f'skill{i+1}_level'] = skill_pts

    writer = create_writer()

    writer.save_base_map_csv(
        "decorations/decoration_base.csv",
        mhdata.decoration_map,
        schema=schema.DecorationBaseSchema(),
        translation_filename="decorations/decoration_base_translations.csv"
    )

    print("Decoration files updated\n")