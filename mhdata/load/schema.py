"""
This module contains marshmallo schema definitions for loaded files.
"""

import collections
from marshmallow import Schema, fields, ValidationError, pre_load, post_dump

from mhdata.util import group_fields, ungroup_fields
from . import cfg

def choice_check(*items):
    def validate_fn(check):
        if check not in items:
            item_str = ", ".join(map(lambda i: i or "None", items))
            raise ValidationError(f"Value {check} not one of ({item_str})")
    return validate_fn

def ValidatedStr(*items):
    return fields.Str(allow_none=True, validate=choice_check(*items))

class BaseSchema(Schema):
    "Base class for all schemas in this project"
    __groups__ = ()
    class Meta:
        ordered = True

    @pre_load
    def group_fields(self, data):
        if not isinstance(data, collections.Mapping):
            raise TypeError("Invalid data type, perhaps you forgot many=true?")
        groups = self.__groups__ or []
        return group_fields(data, groups=groups)

    @post_dump
    def ungroup_fields(self, data):
        groups = self.__groups__ or []
        return ungroup_fields(data, groups=groups)


# schemas were added later down the line, so no schemas exist for certain objects yet
# schemas are used mostly for type conversion and pre-validation

class ItemSchema(BaseSchema):
    __groups__ = ('name', 'description')
    name = fields.Dict()
    description = fields.Dict()
    category = ValidatedStr("item", "material", "ammo", "misc", "hidden")
    subcategory = ValidatedStr(None, "account", "supply", "appraisal", "trade")
    rarity = fields.Int(allow_none=True, default=0)
    buy_price = fields.Int(allow_none=True)
    sell_price = fields.Int(allow_none=True)
    points = fields.Int(allow_none=True)
    carry_limit = fields.Int(allow_none=True)
    
    icon_name = fields.Str(allow_none=True)
    icon_color = ValidatedStr(None, *cfg.icon_colors)

class ItemCombinationSchema(BaseSchema):
    id = fields.Int()
    result = fields.Str()
    first = fields.Str()
    second = fields.Str(allow_none=True)
    quantity = fields.Int()

class LocationSchema(BaseSchema):
    __groups__ = ('name',)
    name = fields.Dict()
    items = fields.Nested('LocationItemEntrySchema', many=True, missing=[])

class LocationItemEntrySchema(BaseSchema):
    area = fields.Int()
    rank = ValidatedStr(*cfg.supported_ranks)
    item_lang = ValidatedStr(*cfg.supported_languages)
    item = fields.Str()
    stack = fields.Int()
    percentage = fields.Int()
    nodes = fields.Int(allow_none=True, default=1)

class SkillSchema(BaseSchema):
    __groups__ = ('name', 'description')
    name = fields.Dict()
    description = fields.Dict()
    icon_color = ValidatedStr(None, *cfg.icon_colors)

    levels = fields.Nested('SkillLevelSchema', many=True, required=True)

class SkillLevelSchema(BaseSchema):
    __groups__ = ('description',)
    level = fields.Int()
    description = fields.Dict()

class ArmorSetSchema(BaseSchema):
    __groups__ = ('name',)
    name = fields.Dict()
    armor_lang = fields.Str()
    rank = ValidatedStr(*cfg.supported_ranks)
    head = fields.Str(allow_none=True)
    chest = fields.Str(allow_none=True)
    arms = fields.Str(allow_none=True)
    waist = fields.Str(allow_none=True)
    legs = fields.Str(allow_none=True)
    bonus = fields.Str(allow_none=True)

class ArmorSetBonus(BaseSchema):
    __groups__ = ('name',)
    name = fields.Dict()
    skill1_name = fields.Str(allow_none=True)
    skill1_required = fields.Int(allow_none=True)
    skill2_name = fields.Str(allow_none=True)
    skill2_required = fields.Int(allow_none=True)

class ArmorBaseSchema(BaseSchema):
    "Schema for armor base data"
    __groups__ = ('name',)
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

class ArmorSchema(ArmorBaseSchema):
    "Schema for complete armor data"
    # the below are unvalidated, but exist so they're retained
    skills = fields.Dict()
    craft = fields.Nested('ArmorCraftSchema', many=False, missing={})

class RecipeSchema(BaseSchema):
    name_en = fields.Str()
    item1_name = fields.Str(allow_none=True)
    item1_qty = fields.Int(allow_none=True)
    item2_name = fields.Str(allow_none=True)
    item2_qty = fields.Int(allow_none=True)
    item3_name = fields.Str(allow_none=True)
    item3_qty = fields.Int(allow_none=True)
    item4_name = fields.Str(allow_none=True)
    item4_qty = fields.Int(allow_none=True)

class ArmorCraftSchema(RecipeSchema):
    pass

class DecorationBaseSchema(BaseSchema):
    __groups__ = ('name',)
    name = fields.Dict()
    rarity = fields.Int()
    skill_en = fields.Str()
    slot = fields.Int()
    icon_color = ValidatedStr(None, *cfg.icon_colors)

class DecorationSchema(DecorationBaseSchema):
    chances = fields.Dict()

class CharmBaseSchema(BaseSchema):
    __groups__ = ('name',)
    id = fields.Int()
    name = fields.Dict()
    previous_en = fields.Str(allow_none=True)
    rarity = fields.Int(allow_none=True)

class CharmSchema(CharmBaseSchema):
    skills = fields.Dict()
    craft = fields.Dict()
