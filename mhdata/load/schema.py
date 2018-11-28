"""
This module contains marshmallow schema definitions for loaded files.
Schemas in this file inherit from a BaseSchema, which is a schema object that supports grouping.
Those in the __groups__ dict are grouped together by prefix, and are usually used for localized dictionaries.
"""

from mhdata import cfg

from marshmallow import fields, ValidationError, validates
from .cfields import ValidatedStr, ExcelBool, BaseSchema, NestedPrefix

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
    monster = fields.Str(allow_none=True)
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
    # note: combination fields are validated in validate.py
    __groups__ = ('name',)
    id = fields.Int()
    name = fields.Dict()
    weapon_type = ValidatedStr(*cfg.weapon_types)
    previous_en = fields.Str(allow_none=True)
    rarity = fields.Int(allow_none=True)
    attack = fields.Int()
    affinity = fields.Int()
    defense = fields.Int(allow_none=True)
    element1 = fields.Str(allow_none=True)
    element1_attack = fields.Int(allow_none=True)
    element2 = fields.Str(allow_none=True)
    element2_attack = fields.Int(allow_none=True)
    element_hidden = ExcelBool()
    elderseal = ValidatedStr(None, 'low', 'average', 'high')
    slot_1 = fields.Int()
    slot_2 = fields.Int()
    slot_3 = fields.Int()
    
    kinsect_bonus = ValidatedStr(None, *cfg.valid_kinsects)
    phial = ValidatedStr(None, *cfg.valid_phials)
    phial_power = fields.Int(allow_none=True)
    shelling = ValidatedStr(None, *cfg.valid_shellings)
    shelling_level = fields.Int(allow_none=True)
    notes = fields.Str(allow_none=True)
    ammo_config = fields.Str(allow_none=True)

    @validates('notes')
    def validate_notes(self, notes_str):
        if not notes_str:
            return # valid, none is allowed

        notes = set(notes_str)
        if len(notes) != 3:
            raise ValidationError(f"Notes must be 3 unique characters")
        
        valid = notes <= set(cfg.valid_notes)
        if not valid: # not a subset of valid notes
            raise ValidationError(f"invalid notes {notes_str}, notes must be subset of {str(cfg.valid_notes)}")

class WeaponSchema(WeaponBaseSchema):
    craft = fields.Nested('WeaponCraftSchema', many=True, default={})
    sharpness = fields.Nested('WeaponSharpnessSchema', many=False, missing=None)
    bow = fields.Nested('WeaponBowSchema', many=False, missing={})
    gun = fields.Nested('WeaponAmmoSchema', many=False, missing={})

class WeaponSharpnessSchema(BaseSchema):
    base_name_en = fields.Str()
    maxed = ExcelBool()
    red = fields.Int()
    orange = fields.Int()
    yellow = fields.Int()
    green = fields.Int()
    blue = fields.Int()
    white = fields.Int()
    purple = fields.Int()

class WeaponCraftSchema(RecipeSchema):
    type = ValidatedStr("Create", "Upgrade")

class WeaponBowSchema(BaseSchema):
    close = fields.Bool()
    power = fields.Bool()
    poison = fields.Bool()
    paralysis = fields.Bool()
    sleep = fields.Bool()
    blast = fields.Bool()

class AmmoGroupSchema(BaseSchema):
    clip = fields.Int()
    rapid = ExcelBool(null_is_false=True, missing=False)
    recoil = fields.Int(allow_none=True)
    reload = ValidatedStr(None, "very slow", "slow", "normal", "fast")

def AmmoGroup():
    return NestedPrefix("AmmoGroupSchema")

class WeaponAmmoSchema(BaseSchema):
    deviation = fields.Str()
    special = fields.Str()
    normal1 = AmmoGroup()
    normal2 = AmmoGroup()
    normal3 = AmmoGroup()
    pierce1 = AmmoGroup()
    pierce2 = AmmoGroup()
    pierce3 = AmmoGroup()
    spread1 = AmmoGroup()
    spread2 = AmmoGroup()
    spread3 = AmmoGroup()
    sticky1 = AmmoGroup()
    sticky2 = AmmoGroup()
    sticky3 = AmmoGroup()
    cluster1 = AmmoGroup()
    cluster2 = AmmoGroup()
    cluster3 = AmmoGroup()
    recover1 = AmmoGroup()
    recover2 = AmmoGroup()
    poison1 = AmmoGroup()
    poison2 = AmmoGroup()
    paralysis1 = AmmoGroup()
    paralysis2 = AmmoGroup()
    sleep1 = AmmoGroup()
    sleep2 = AmmoGroup()
    exhaust1 = AmmoGroup()
    exhaust2 = AmmoGroup()
    flaming = AmmoGroup()
    water = AmmoGroup()
    freeze = AmmoGroup()
    thunder = AmmoGroup()
    dragon = AmmoGroup()
    slicing = AmmoGroup()
    wyvern = AmmoGroup()
    demon = AmmoGroup()
    armor = AmmoGroup()
    tranq = AmmoGroup()

class WeaponMelodySchema(BaseSchema):
    __groups__ = ('effect1', 'effect2')
    notes = fields.String()
    duration = fields.String()
    extension = fields.String()
    effect1 = fields.Dict()
    effect2 = fields.Dict()

class QuestSchema(BaseSchema):
    __groups__ = ("name",)
    name = fields.Dict(allow_none=True)
    classification = fields.String(allow_none=True)
    client = fields.Dict(allow_none=True)
    location = fields.String(allow_none=True)
    difficulty = fields.Int(allow_none=True)
    clear_type = fields.String(allow_none=True)
    hunter_rank = fields.Int(allow_none=True)
    time_limit = fields.Int(allow_none=True)
    faint_limit = fields.Int(allow_none=True)
    zeni_reward = fields.Int(allow_none=True)
    request_text = fields.Dict(allow_none=True)
    target_text = fields.Dict(allow_none=True)
    miss_text = fields.Dict(allow_none=True)
