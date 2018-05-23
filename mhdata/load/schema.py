from marshmallow import Schema, fields, ValidationError

from .cfg import *

def choice_check(*items):
    def validate_fn(check):
        if check not in items:
            item_str = ", ".join(items)
            raise ValidationError(f"Value {check} not one of ({item_str})")
    return validate_fn

def ValidatedStr(*items):
    return fields.Str(validate=choice_check(*items))

class ItemSchema(Schema):
    name = fields.Dict()
    description = fields.Dict()
    category = ValidatedStr("items", "material", "account", "ammo")
    rarity = fields.Int(allow_none=True, default=0)
    buy_price = fields.Int(allow_none=True)
    sell_price = fields.Int(allow_none=True)
    carry_limit = fields.Int(allow_none=True)

class LocationSchema(Schema):
    name = fields.Dict()
    items = fields.Nested('LocationItemEntry', many=True, missing=[])

class LocationItemEntry(Schema):
    location_en = fields.Dict()
    area = fields.Int()
    rank = ValidatedStr(*supported_ranks)
    item_lang = ValidatedStr(*supported_languages)
    item = fields.Str()
    stack = fields.Int()
    percentage = fields.Int()

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