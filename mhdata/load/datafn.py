"""
A collection of functions designed to handle data read from mhdata.load.
"""

from mhdata import cfg

def iter_setbonus_skills(setbonus):
    "Iterates over set bonuses, returning (name, required) tuples"
    for idx in range(1, cfg.max_skill_count + 1):
        name = setbonus[f'skill{idx}_name']
        required = setbonus[f'skill{idx}_required']

        if not name:
            break

        yield (name, required)


def iter_skill_points(obj):
    "Iterates over armor/weapon skill points, returning (name, lvl) tuples"
    for idx in range(1, cfg.max_skill_count + 1):
        name = obj['skills'][f'skill{idx}_name']
        points = obj['skills'][f'skill{idx}_pts']

        if not name:
            break

        yield (name, points)

def iter_armorset_pieces(armorset):
    "Iterates over the armor pieces of a set, returning (part, name) tuples"
    for part in cfg.armor_parts:
        if not armorset[part]:
            continue
        yield (part, armorset[part])

def iter_armor_recipe(armor):
    "Iterates over the items in an armor recipe, returning (name, qty) tuples"
    for idx in range(1, cfg.max_recipe_item_count + 1):
        item_name = armor['craft'][f'item{idx}_name']
        quantity = armor['craft'][f'item{idx}_qty']
        
        if not item_name:
            break

        yield (item_name, quantity)

def iter_weapon_recipe(recipe):
    "Iterates over the items in a weapon recipe, returning (name, qty) tuples"
    for idx in range(1, cfg.max_recipe_item_count + 1):
        item_name = recipe[f'item{idx}_name']
        quantity = recipe[f'item{idx}_qty']
        
        if not item_name:
            break

        yield (item_name, quantity)

def merge_sharpness(weapon):
    s = weapon['sharpness']
    values = (s['red'], s['orange'], s['yellow'],
                s['green'], s['blue'], s['white'], s['purple'])
    return ",".join((str(v) for v in values))