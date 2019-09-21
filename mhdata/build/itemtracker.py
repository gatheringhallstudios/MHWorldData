class ItemTracker:
    def __init__(self, mhdata):
        self.all_items = {}
        self.all_items_rev = {}
        for entry in mhdata.item_map.values():
            if entry['buy_price'] or entry['subcategory'] in ('trade', 'account', 'supply'):
                continue
            self.all_items[entry.id] = entry['name']['en']
            self.all_items_rev[entry['name']['en']] = entry.id

    def mark_encountered_name(self, item_name):
        item_id = self.all_items_rev.get(item_name, None)
        if item_id is not None:
            del self.all_items_rev[item_name]
            del self.all_items[item_id]

    def mark_encountered_id(self, item_id):
        item_name = self.all_items.get(item_id, None)
        if item_name is not None:
            del self.all_items_rev[item_name]
            del self.all_items[item_id]

    def print_unmarked(self):
        num_unmarked = len(self.all_items)
        if num_unmarked > 0:
            print("\nWarning: These items are unlinked and do not drop from any source")
            for name in self.all_items.values():
                print(name)

            print(f"\nThere are {num_unmarked} items with no drop source\n")