"""
This module contains marshmallo schema definitions for loaded files.
"""

import collections
from marshmallow import Schema, fields, ValidationError, pre_load, post_dump

from mhdata.util import group_fields, ungroup_fields
from mhdata import cfg

from .cfields import ValidatedStr, ExcelBool

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
    camps = fields.Nested('LocationCampSchema', many=True, missing=[])

class LocationItemEntrySchema(BaseSchema):
    area = fields.Int()
    rank = ValidatedStr(None, *cfg.supported_ranks)
    item_lang = ValidatedStr(*cfg.supported_languages)
    item = fields.Str()
    stack = fields.Int()
    percentage = fields.Int()
    nodes = fields.Int(allow_none=True, default=1)

class LocationCampSchema(BaseSchema):
    __groups__ = ('name',)
    base_name_en = fields.Str()
    name = fields.Dict()
    area = fields.Int()

class MonsterSchema(BaseSchema):
    __groups__ = ('name', 'description', 'ecology')
    name = fields.Dict()
    description = fields.Dict()
    ecology = fields.Dict()
    size = ValidatedStr('small', 'large')

    # most sub-items are currently unvalidated
    # todo: create schema entries for the below
    weaknesses = fields.Dict()
    hitzones = fields.List(fields.Dict())
    breaks = fields.List(fields.Dict())
    habitats = fields.List(fields.Dict())
    rewards = fields.List(fields.Dict())
    ailments = fields.Nested('MonsterAilments', many=False)

class MonsterAilments(BaseSchema):
    roar = ValidatedStr(None, 'small', 'large')
    wind = ValidatedStr(None, 'small', 'large', 'extreme')
    tremor = ValidatedStr(None, "small", "large")
    defense_down = ExcelBool(null_is_false=True)
    fireblight = ExcelBool(null_is_false=True)
    waterblight = ExcelBool(null_is_false=True)
    thunderblight = ExcelBool(null_is_false=True)
    iceblight = ExcelBool(null_is_false=True)
    dragonblight = ExcelBool(null_is_false=True)
    blastblight = ExcelBool(null_is_false=True)
    poison = ExcelBool(null_is_false=True)
    sleep = ExcelBool(null_is_false=True)
    paralysis = ExcelBool(null_is_false=True)
    bleed = ExcelBool(null_is_false=True)
    stun = ExcelBool(null_is_false=True)
    mud = ExcelBool(null_is_false=True)
    effluvia = ExcelBool(null_is_false=True)

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

class WeaponBaseSchema(BaseSchema):
    __groups__ = ('name',)
    id = fields.Int()
    name = fields.Dict()
    weapon_type = fields.Str() # todo: replace for validated str
    previous_en = fields.Str(allow_none=True)
    rarity = fields.Int(allow_none=True)
    attack = fields.Int()
    defense = fields.Int(allow_none=True)
    element1 = fields.Str(allow_none=True)
    element1_attack = fields.Int(allow_none=True)
    element2 = fields.Str(allow_none=True)
    element2_attack = fields.Int(allow_none=True)
    element_hidden = ExcelBool()
    slot_1 = fields.Int()
    slot_2 = fields.Int()
    slot_3 = fields.Int()
    
    kinsect_bonus = ValidatedStr(None, *cfg.valid_kinsects)
    phial = ValidatedStr(None, *cfg.valid_phials)
    phial_power = fields.Int(allow_none=True)
    shelling = ValidatedStr(None, *cfg.valid_shellings)
    shelling_level = fields.Int(allow_none=True)

class WeaponSchema(WeaponBaseSchema):
    craft = fields.Nested('WeaponCraftSchema', many=True, missing={})
    bow = fields.Nested('WeaponBowSchema', many=False, missing={})
    gun = fields.Nested('WeaponGunSchema', many=False, missing={})

class WeaponCraftSchema(RecipeSchema):
    type = ValidatedStr("Create", "Upgrade")

class WeaponBowSchema(BaseSchema):
    close = fields.Bool()
    power = fields.Bool()
    poison = fields.Bool()
    paralysis = fields.Bool()
    sleep = fields.Bool()
    blast = fields.Bool()

class WeaponGunSchema(BaseSchema):
    deviation = fields.Str()
    special = fields.Str()
    normal_1 = fields.Int()
    normal_2 = fields.Int()
    normal_3 = fields.Int()
    pierce_1 = fields.Int()
    pierce_2 = fields.Int()
    pierce_3 = fields.Int()
    spread_1 = fields.Int()
    spread_2 = fields.Int()
    spread_3 = fields.Int()
    sticky_1 = fields.Int()
    sticky_2 = fields.Int()
    sticky_3 = fields.Int()
    cluster_1 = fields.Int()
    cluster_2 = fields.Int()
    cluster_3 = fields.Int()
    recover_1 = fields.Int()
    recover_2 = fields.Int()
    poison_1 = fields.Int()
    poison_2 = fields.Int()
    paralysis_1 = fields.Int()
    paralysis_2 = fields.Int()
    sleep_1 = fields.Int()
    sleep_2 = fields.Int()
    exhaust_1 = fields.Int()
    exhaust_2 = fields.Int()
    flaming = fields.Int()
    water = fields.Int()
    freeze = fields.Int()
    thunder = fields.Int()
    dragon = fields.Int()
    slicing = fields.Int()
    wyvern = fields.Int()
    demon = fields.Int()
    armor = fields.Int()
    tranq = fields.Int()
