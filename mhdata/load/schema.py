"""
This module contains marshmallow schema definitions for loaded files.
Schemas in this file inherit from a BaseSchema, which is a schema object that supports grouping.
Those in the __groups__ dict are grouped together by prefix, and are usually used for localized dictionaries.
"""

from mhdata import cfg

from marshmallow import fields, ValidationError, validates, validates_schema
from .cfields import ValidatedStr, ExcelBool, BaseSchema, NestedPrefix

# schemas were added later down the line, so no schemas exist for certain objects yet
# schemas are used mostly for type conversion and pre-validation

class ItemSchema(BaseSchema):
    __groups__ = ('name', 'description')
    id = fields.Int()
    name = fields.Dict()
    description = fields.Dict()
    category = ValidatedStr("item", "material", "ammo", "misc", "hidden")
    subcategory = ValidatedStr(None, "account", "supply", "appraisal", "trade")
    rarity = fields.Int(allow_none=True, default=0)
    buy_price = fields.Int(allow_none=True)
    sell_price = fields.Int(allow_none=True)
    carry_limit = fields.Int(allow_none=True)
    points = fields.Int(allow_none=True)
    
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

class MonsterBaseSchema(BaseSchema):
    __groups__ = ('name', 'description')
    id = fields.Int()
    name = fields.Dict()
    description = fields.Dict()
    ecology_en = fields.Str(allow_none=True)
    size = ValidatedStr('small', 'large')
    pitfall_trap = ExcelBool(null_is_false=True)
    shock_trap = ExcelBool(null_is_false=True)
    vine_trap = ExcelBool(null_is_false=True)

class MonsterSchema(MonsterBaseSchema):
    # most sub-items are currently unvalidated
    # todo: create schema entries for the below
    weaknesses = fields.List(fields.Dict())
    hitzones = fields.Nested('MonsterHitzone', many=True)
    breaks = fields.List(fields.Dict())
    habitats = fields.List(fields.Dict())
    rewards = fields.Nested('MonsterReward', many=True)
    ailments = fields.Nested('MonsterAilments', many=False)

class MonsterHitzone(BaseSchema):
    hitzone = fields.Dict()
    cut = fields.Int()
    impact = fields.Int()
    shot = fields.Int()
    fire = fields.Int()
    water = fields.Int()
    thunder = fields.Int()
    ice = fields.Int()
    dragon = fields.Int()
    ko = fields.Int()

class MonsterReward(BaseSchema):
    condition_en = fields.Str()
    rank = ValidatedStr(*cfg.supported_ranks)
    item_en = fields.Str()
    stack = fields.Int()
    percentage = fields.Int(allow_none=True)

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
    regional = ExcelBool(null_is_false=True)
    poison = ExcelBool(null_is_false=True)
    sleep = ExcelBool(null_is_false=True)
    paralysis = ExcelBool(null_is_false=True)
    bleed = ExcelBool(null_is_false=True)
    stun = ExcelBool(null_is_false=True)
    mud = ExcelBool(null_is_false=True)
    effluvia = ExcelBool(null_is_false=True)

class SkillBaseSchema(BaseSchema):
    __groups__ = ('name', 'description')
    name = fields.Dict()
    description = fields.Dict()
    icon_color = ValidatedStr(None, *cfg.icon_colors)
    secret = fields.Int(allow_none=True)
    unlocks = fields.String(allow_none=True)

class SkillSchema(SkillBaseSchema):
    levels = fields.Nested('SkillLevelSchema', many=True, required=True)

class SkillLevelSchema(BaseSchema):
    __groups__ = ('description',)
    base_name_en = fields.Str()
    level = fields.Int()
    description = fields.Dict()

class RecipeSchema(BaseSchema):
    base_name_en = fields.Str()
    item1_name = fields.Str(allow_none=True)
    item1_qty = fields.Int(allow_none=True)
    item2_name = fields.Str(allow_none=True)
    item2_qty = fields.Int(allow_none=True)
    item3_name = fields.Str(allow_none=True)
    item3_qty = fields.Int(allow_none=True)
    item4_name = fields.Str(allow_none=True)
    item4_qty = fields.Int(allow_none=True)

class WeaponRecipeSchema(BaseSchema):
    base_name_en = fields.Str()
    weapon_type = ValidatedStr(*cfg.weapon_types)
    type = ValidatedStr("Create", "Upgrade")
    item1_name = fields.Str(allow_none=True)
    item1_qty = fields.Int(allow_none=True)
    item2_name = fields.Str(allow_none=True)
    item2_qty = fields.Int(allow_none=True)
    item3_name = fields.Str(allow_none=True)
    item3_qty = fields.Int(allow_none=True)
    item4_name = fields.Str(allow_none=True)
    item4_qty = fields.Int(allow_none=True)


class CharmRecipeSchema(BaseSchema):
    base_name_en = fields.Str()
    type = ValidatedStr("Create", "Upgrade")
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
    id = fields.Int()
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
    craft = fields.Nested('RecipeSchema', many=False, missing={})

class DecorationBaseSchema(BaseSchema):
    __groups__ = ('name',)
    id = fields.Int()
    name = fields.Dict()
    slot = fields.Int()
    rarity = fields.Int()
    skill1_name = fields.Str()
    skill1_level = fields.Int()
    skill2_name = fields.Str(allow_none=True)
    skill2_level = fields.Int(allow_none=True)
    icon_color = ValidatedStr(None, *cfg.icon_colors)

    @validates_schema
    def validate_skill2(self, data):
        if bool(data['skill2_level']) != bool(data['skill2_name']):
            raise ValidationError(f"Skill2 points and name must both be null or not null")

class DecorationSchema(DecorationBaseSchema):
    chances = fields.Dict()

class CharmBaseSchema(BaseSchema):
    __groups__ = ('name',)
    id = fields.Int()
    name = fields.Dict()
    previous_en = fields.Str(allow_none=True)
    rarity = fields.Int(allow_none=True)
    skill1_name = fields.Str()
    skill1_level = fields.Int()
    skill2_name = fields.Str(allow_none=True)
    skill2_level = fields.Int(allow_none=True)
    
    @validates_schema
    def validate_skill2(self, data):
        if bool(data.get('skill2_level')) != bool(data.get('skill2_name')):
            raise ValidationError(f"Skill2 points and name must both be null or not null")

class CharmSchema(CharmBaseSchema):
    craft = fields.Nested('WeaponRecipeSchema', many=True, default={})

class WeaponBaseSchema(BaseSchema):
    # note: combination fields are validated in validate.py
    __groups__ = ('name',)
    id = fields.Int()
    name = fields.Dict()
    weapon_type = ValidatedStr(*cfg.weapon_types)
    previous_en = fields.Str(allow_none=True)
    category = fields.Str(allow_none=True)
    rarity = fields.Int(allow_none=True)
    attack = fields.Int()
    affinity = fields.Int()
    defense = fields.Int(allow_none=True)
    element_hidden = ExcelBool()
    element1 = fields.Str(allow_none=True)
    element1_attack = fields.Int(allow_none=True)
    element2 = fields.Str(allow_none=True)
    element2_attack = fields.Int(allow_none=True)
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
    skill = fields.Str(allow_none=True)

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
    craft = fields.Nested('WeaponRecipeSchema', many=True, default={})
    sharpness = fields.Nested('WeaponSharpnessSchema', many=False, missing=None)
    bow = fields.Nested('WeaponBowSchema', many=False, missing={})
    gun = fields.Nested('WeaponAmmoSchema', many=False, missing={})

class WeaponSharpnessSchema(BaseSchema):
    base_name_en = fields.Str()
    weapon_type = ValidatedStr(*cfg.weapon_types)
    maxed = ExcelBool()
    red = fields.Int()
    orange = fields.Int()
    yellow = fields.Int()
    green = fields.Int()
    blue = fields.Int()
    white = fields.Int()
    purple = fields.Int()

class WeaponBowSchema(BaseSchema):
    base_name_en = fields.Str()
    weapon_type = ValidatedStr(*cfg.weapon_types)
    close = ExcelBool()
    power = ExcelBool()
    paralysis = ExcelBool()
    poison = ExcelBool()
    sleep = ExcelBool()
    blast = ExcelBool()

class AmmoGroupSchema(BaseSchema):
    clip = fields.Int()
    rapid = ExcelBool(null_is_false=True, missing=False)
    recoil = fields.Int(allow_none=True)
    reload = ValidatedStr(None, "very slow", "slow", "normal", "fast")

def AmmoGroup():
    return NestedPrefix("AmmoGroupSchema")

class WeaponAmmoSchema(BaseSchema):
    key = fields.Str()
    weapon_type = ValidatedStr(*cfg.weapon_types)
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

class WeaponMelodyBaseSchema(BaseSchema):
    __groups__ = ('name', 'effect1', 'effect2')
    id = fields.Int()
    name = fields.Dict()
    effect1 = fields.Dict()
    effect2 = fields.Dict()
    duration = fields.String()
    extension = fields.String()

class WeaponMelodySchema(WeaponMelodyBaseSchema):
    notes = fields.Nested("WeaponMelodyNotesSchema", many=True)

class WeaponMelodyNotesSchema(BaseSchema):
    base_name_en = fields.String()
    notes = fields.String()

class KinsectBaseSchema(BaseSchema):
    __groups__ = ('name',)
    id = fields.Int()
    name = fields.Dict()
    previous_en = fields.Str(allow_none=True)
    rarity = fields.Int()
    attack_type = fields.String()
    dust_effect = fields.String()
    power = fields.Int()
    speed = fields.Int()
    heal = fields.Int()

class KinsectSchema(KinsectBaseSchema):
    craft = fields.Nested('RecipeSchema', many=False, missing={})

class QuestBaseSchema(BaseSchema):
    __groups__ = ('name','objective','description')
    id = fields.Int()
    name = fields.Dict()
    objective = fields.Dict()
    description = fields.Dict()
    category = fields.String(allow_none=True)
    rank = fields.Str()
    stars = fields.Int()
    quest_type = ValidatedStr(None, 'hunt', 'capture', 'deliver', 'assignment')
    location_en = fields.String(allow_none=True)
    zenny = fields.Int(allow_none=True)

class QuestSchema(QuestBaseSchema):
    monsters = fields.Nested('QuestMonster', many=True, missing=[])
    rewards = fields.Nested('QuestReward', many=True, missing=[])

class QuestMonster(BaseSchema):
    monster_en = fields.String()
    quantity = fields.Int()
    is_objective = ExcelBool()

class QuestReward(BaseSchema):
    group = fields.String()
    item_en = fields.String()
    stack = fields.Integer()
    percentage = fields.Integer()

class ToolSchema(BaseSchema):
    __groups__ = ('name','name_base','description')
    id = fields.Int()
    name = fields.Dict()
    name_base = fields.Dict()
    description = fields.Dict()
    tool_type = ValidatedStr('mantle', 'booster')
    duration = fields.Int()
    duration_upgraded = fields.Int(allow_none=True)
    recharge = fields.Int()
    slot_1 = fields.Int()
    slot_2 = fields.Int()
    slot_3 = fields.Int()
    icon_color = ValidatedStr(None, *cfg.icon_colors)