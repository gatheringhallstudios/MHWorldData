"""
This module contains marshmallo schema definitions for loaded files.
"""

from marshmallow import Schema, fields, ValidationError

from .cfg import *

def choice_check(*items):
    def validate_fn(check):
        if check not in items:
            item_str = ", ".join(items)
            raise ValidationError(f"Value {check} not one of ({item_str})")
    return validate_fn

def ValidatedStr(*items):
    return fields.Str(allow_none=True, validate=choice_check(*items))


class ItemSchema(Schema):
    name = fields.Dict()
    description = fields.Dict()
    category = ValidatedStr("item", "material", "ammo", "misc", "hidden")
    subcategory = ValidatedStr(None, "account", "supply")
    rarity = fields.Int(allow_none=True, default=0)
    buy_price = fields.Int(allow_none=True)
    sell_price = fields.Int(allow_none=True)
    carry_limit = fields.Int(allow_none=True)

class ItemCombinationSchema(Schema):
    id = fields.Int()
    result = fields.Str()
    first = fields.Str()
    second = fields.Str(allow_none=True)
    quantity = fields.Int()

class LocationSchema(Schema):
    name = fields.Dict()
    items = fields.Nested('LocationItemEntry', many=True, missing=[])

class LocationItemEntry(Schema):
    area = fields.Int()
    rank = ValidatedStr(*supported_ranks)
    item_lang = ValidatedStr(*supported_languages)
    item = fields.Str()
    stack = fields.Int()
    percentage = fields.Int()

class ArmorSetSchema(Schema):
    name = fields.Dict()
    armor_lang = fields.Str()
    head = fields.Str(allow_none=True)
    chest = fields.Str(allow_none=True)
    arms = fields.Str(allow_none=True)
    waist = fields.Str(allow_none=True)
    legs = fields.Str(allow_none=True)
    bonus = fields.Str(allow_none=True)

class ArmorSetBonus(Schema):
    name = fields.Dict()
    skills = fields.Nested('ArmorSetBonusSkill', many=True)

class ArmorSetBonusSkill(Schema):
    skill = fields.String()
    points = fields.Int()
    threshold = fields.Int()

class ArmorSchema(Schema):
    name = fields.Dict()
    rarity = fields.Int()
    type = ValidatedStr('head', 'chest', 'arms', 'waist', 'legs')
    gender = ValidatedStr('male', 'female', 'both')
    slot_1 = fields.Int()
    slot_2 = fields.Int()
    slot_3 = fields.Int()
    defense_base = fields.Int(validate=lambda n: n > 0)
    defense_max = fields.Int(validate=lambda n: n > 0)
    defense_augment_max = fields.Int(validate=lambda n: n > 0)
    defense_fire = fields.Int()
    defense_water = fields.Int()
    defense_thunder = fields.Int()
    defense_ice = fields.Int()
    defense_dragon = fields.Int()

    # the below are unvalidated, but exist so they're retained
    skills = fields.Dict()
    craft = fields.Dict()