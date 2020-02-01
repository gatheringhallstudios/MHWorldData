from typing import Iterable, Tuple

def convert_recipe(item_updater, recipe_items: Iterable[Tuple[int, int]]):
    data = {}
    for i in range(1, 5):
        data[f'item{i}_name'] = None
        data[f'item{i}_qty'] = None
    
    for i, (item_id, item_qty) in enumerate(recipe_items):
        data[f'item{i+1}_name'] = item_updater.name_for(item_id)['en']
        data[f'item{i+1}_qty'] = item_qty

    return data