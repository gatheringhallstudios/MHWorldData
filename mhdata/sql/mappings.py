# Defines SQL objects.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, Text, Boolean
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

Base = declarative_base()

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    category = Column(Text)
    subcategory = Column(Text)
    rarity = Column(Integer)
    buy_price = Column(Integer)
    sell_price = Column(Integer)
    carry_limit = Column(Integer)
    points = Column(Integer)

    icon_name = Column(Text)
    icon_color = Column(Text)

    translations = relationship("ItemText")

class ItemText(Base):
    __tablename__ = "item_text"
    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)
    description = Column(Text)

class ItemCombination(Base):
    __tablename__ = "item_combination"
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('item.id'))
    first_id = Column(Integer, ForeignKey('item.id'))
    second_id = Column(Integer, ForeignKey('item.id'))
    quantity = Column(Integer)

class Language(Base):
    __tablename__ = 'language'
    id = Column(Text, primary_key=True)
    name = Column(Text)
    is_complete = Column(Text)

class Location(Base):
    __tablename__ = 'location_text'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

class LocationItem(Base):
    __tablename__ = 'location_item'

    # note: it is possible for there to be multiple entries of the same thing.
    # therefore, this join-table has no "real id" and uses a surrogate instead
    id = Column(Integer, primary_key=True, autoincrement=True)

    location_id = Column(Integer, ForeignKey("location_text.id"))
    area = Column(Integer)
    rank = Column(Text)
    item_id = Column(Integer, ForeignKey('item.id'), index=True)
    stack = Column(Integer)
    percentage = Column(Integer)
    nodes = Column(Integer, default=1, nullable=False)

class LocationCamp(Base):
    """Defines a location camp and a name entry. 
    As this has limited data, its the text entry as well"""
    __tablename__ = 'location_camp_text'

    # This join-table has no "real id" and uses a surrogate instead
    id = Column(Integer, primary_key=True, autoincrement=True)

    location_id = Column(Integer, ForeignKey("location_text.id"))
    lang_id = Column(Text, ForeignKey('language.id'))
    name = Column(Text)
    area = Column(Integer)

class Monster(Base):
    __tablename__ = 'monster'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, unique=True)
    size = Column(Text)
    icon = Column(Text)

    has_weakness = Column(Boolean, default=False)
    has_alt_weakness = Column(Boolean, default=False)

    weakness_fire = Column(Integer)
    weakness_water = Column(Integer)
    weakness_ice = Column(Integer)
    weakness_thunder = Column(Integer)
    weakness_dragon = Column(Integer)

    weakness_poison = Column(Integer)
    weakness_sleep = Column(Integer)
    weakness_paralysis = Column(Integer)
    weakness_blast = Column(Integer)
    weakness_stun = Column(Integer)

    alt_weakness_fire = Column(Integer)
    alt_weakness_water = Column(Integer)
    alt_weakness_ice = Column(Integer)
    alt_weakness_thunder = Column(Integer)
    alt_weakness_dragon = Column(Integer)

    ailment_roar = Column(Text)
    ailment_wind = Column(Text)
    ailment_tremor = Column(Text)
    ailment_defensedown = Column(Boolean)
    ailment_fireblight = Column(Boolean)
    ailment_waterblight = Column(Boolean)
    ailment_thunderblight = Column(Boolean)
    ailment_iceblight = Column(Boolean)
    ailment_dragonblight = Column(Boolean)
    ailment_blastblight = Column(Boolean)
    ailment_poison = Column(Boolean)
    ailment_sleep = Column(Boolean)
    ailment_paralysis = Column(Boolean)
    ailment_bleed = Column(Boolean)
    ailment_stun = Column(Boolean)
    ailment_mud = Column(Boolean)
    ailment_effluvia = Column(Boolean)

    translations = relationship("MonsterText")
    hitzones = relationship("MonsterHitzone")
    breaks = relationship("MonsterBreak")
    rewards = relationship("MonsterReward")
    habitats = relationship("MonsterHabitat")

class MonsterText(Base):
    __tablename__ = 'monster_text'

    id = Column(Integer, ForeignKey('monster.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)
    ecology = Column(Text)
    description = Column(Text)
    alt_state_description = Column(Text)

class MonsterHabitat(Base):
    __tablename__ = 'monster_habitat'
    __table_args__ = (
        UniqueConstraint('monster_id', 'location_id'),
    )
    
    id = Column(Integer, primary_key=True)
    
    monster_id = Column(Integer, ForeignKey('monster.id'), index=True)
    location_id = Column(Integer, ForeignKey('location_text.id'), index=True)
    
    start_area = Column(Text)
    move_area = Column(Text)
    rest_area = Column(Text)

class MonsterHitzone(Base):
    __tablename__ = 'monster_hitzone'

    id = Column(Integer, primary_key=True)

    monster_id = Column(Integer, ForeignKey('monster.id'), index=True)

    cut = Column(Integer)
    impact = Column(Integer)
    shot = Column(Integer)
    fire = Column(Integer)
    water = Column(Integer)
    ice = Column(Integer)
    thunder = Column(Integer)
    dragon = Column(Integer)
    ko = Column(Integer)
    
    translations = relationship("MonsterHitzoneText")

class MonsterHitzoneText(Base):
    __tablename__ = 'monster_hitzone_text'
    id = Column(Integer, ForeignKey('monster_hitzone.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

class MonsterBreak(Base):
    __tablename__ = 'monster_break'

    id = Column(Integer, primary_key=True)

    monster_id = Column(Integer, ForeignKey('monster.id'), index=True)

    flinch = Column(Integer)
    wound = Column(Integer)
    sever = Column(Integer)
    extract = Column(Text)

    translations = relationship("MonsterBreakText")

class MonsterBreakText(Base):
    __tablename__ = 'monster_break_text'
    id = Column(Integer, ForeignKey('monster_break.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    part_name = Column(Text)

class MonsterReward(Base):
    __tablename__ = 'monster_reward'
 
    # note: it is possible for there to be multiple entries of the same thing.
    # therefore, this join-table has no "real id" and uses a surrogate instead
    id = Column(Integer, primary_key=True, autoincrement=True)

    monster_id = Column(Integer, ForeignKey('monster.id'), index=True)
    condition_id = Column(Integer, ForeignKey('monster_reward_condition_text.id'))
    
    rank = Column(Text)
    item_id = Column(Integer, ForeignKey('item.id'), index=True)
    
    stack = Column(Integer)
    percentage = Column(Integer)
    
    condition_translations = relationship("MonsterRewardConditionText", uselist=True)

class MonsterRewardConditionText(Base):
    __tablename__ = 'monster_reward_condition_text'
    id = Column(Integer, primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

class SkillTree(Base):
    __tablename__ = 'skilltree'

    id = Column(Integer, primary_key=True)
    max_level = Column(Integer)
    icon_color = Column(Text)

    translations = relationship("SkillTreeText")
    skills = relationship("Skill")

class SkillTreeText(Base):
    __tablename__ = 'skilltree_text'
    id = Column(Integer, ForeignKey('skilltree.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)
    description = Column(Text)

class Skill(Base):
    "Represents a skill in a skill tree. These are tied to a language"
    __tablename__ = 'skill'
    skilltree_id = Column(Integer, ForeignKey('skilltree.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    level = Column(Integer, primary_key=True)
    description = Column(Text)

class ArmorSet(Base):
    __tablename__ = "armorset"
    id = Column(Integer, primary_key=True)
    rank = Column(Text)
    armorset_bonus_id = Column(Integer)

    translations = relationship("ArmorSetText")
    armor = relationship("Armor")

class ArmorSetText(Base):
    __tablename__ = "armorset_text"
    id = Column(Integer, ForeignKey('armorset.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

class ArmorSetBonusText(Base):
    __tablename__ = "armorset_bonus_text"
    id = Column(Integer, primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)
    description = Column(Text)

class ArmorSetBonusSkill(Base):
    __tablename__ = "armorset_bonus_skill"
    setbonus_id = Column(Integer, primary_key=True)
    skilltree_id = Column(Integer, ForeignKey('skilltree.id'), primary_key=True)
    required = Column(Integer)

class Armor(Base):
    __tablename__ = "armor"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    rarity = Column(Integer)
    rank = Column(Text)
    armor_type = Column(Text)
    armorset_id = Column(Integer, ForeignKey("armorset.id"))
    armorset_bonus_id = Column(Integer)

    male = Column(Boolean)
    female = Column(Boolean)
    slot_1 = Column(Integer)
    slot_2 = Column(Integer)
    slot_3 = Column(Integer)
    defense_base = Column(Integer)
    defense_max = Column(Integer)
    defense_augment_max = Column(Integer)
    fire = Column(Integer)
    water = Column(Integer)
    thunder = Column(Integer)
    ice = Column(Integer)
    dragon = Column(Integer)

    translations = relationship("ArmorText")
    skills = relationship("ArmorSkill")
    craft_items = relationship("ArmorRecipe")

    armorset = relationship("ArmorSet", back_populates="armor")

class ArmorText(Base):
    __tablename__ = "armor_text"
    id = Column(Integer, ForeignKey('armor.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

class ArmorSkill(Base):
    __tablename__ = 'armor_skill'
    armor_id = Column(Integer, ForeignKey('armor.id'), primary_key=True)
    skilltree_id = Column(Integer, ForeignKey('skilltree.id'), primary_key=True)
    level = Column(Integer)

class ArmorRecipe(Base):
    __tablename__ = 'armor_recipe'
    armor_id = Column(Integer, ForeignKey('armor.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    quantity = Column(Integer)

class Weapon(Base):
    __tablename__ = "weapon"
    id = Column(Integer, primary_key=True)
    weapon_type = Column(Text)
    rarity = Column(Integer)
    
    attack = Column(Integer)
    affinity = Column(Integer)
    defense = Column(Integer)
    slot_1 = Column(Integer)
    slot_2 = Column(Integer)
    slot_3 = Column(Integer)

    element1 = Column(Text)
    element1_attack = Column(Integer)
    element2 = Column(Text)
    element2_attack = Column(Integer)
    element_hidden = Column(Boolean)
    elderseal = Column(Text)

    sharpness = Column(Text)
    sharpness_maxed = Column(Boolean)

    previous_weapon_id = Column(ForeignKey("weapon.id"), nullable=True)
    craftable = Column(Boolean, default=False)
    final = Column(Boolean, default=False)

    kinsect_bonus = Column(Text)
    phial = Column(Text)
    phial_power = Column(Integer)
    shelling = Column(Text)
    shelling_level = Column(Integer)
    notes = Column(Text)

    coating_close = Column(Integer)
    coating_power = Column(Integer)
    coating_poison = Column(Integer)
    coating_paralysis = Column(Integer)
    coating_sleep = Column(Integer)
    coating_blast = Column(Integer)

    ammo_id = Column(Integer, ForeignKey('weapon_ammo.id'))

    translations = relationship("WeaponText")
    ammo = relationship("WeaponAmmo")

    # TODO: Find a way to create two relationships: one to craft, one to upgrade.
    # the above will require more sqlalchemy knowledge that unfortunately I don't have.

class WeaponText(Base):
    __tablename__ = "weapon_text"
    id = Column(Integer, ForeignKey('weapon.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

class WeaponAmmo(Base):
    __tablename__ = "weapon_ammo"
    id = Column(Integer, primary_key=True)
    deviation = Column(Text)
    special_ammo = Column(Text)
    normal1_clip = Column(Integer)
    normal2_clip = Column(Integer)
    normal3_clip = Column(Integer)
    pierce1_clip = Column(Integer)
    pierce2_clip = Column(Integer)
    pierce3_clip = Column(Integer)
    spread1_clip = Column(Integer)
    spread2_clip = Column(Integer)
    spread3_clip = Column(Integer)
    sticky1_clip = Column(Integer)
    sticky2_clip = Column(Integer)
    sticky3_clip = Column(Integer)
    cluster1_clip = Column(Integer)
    cluster2_clip = Column(Integer)
    cluster3_clip = Column(Integer)
    recover1_clip = Column(Integer)
    recover2_clip = Column(Integer)
    poison1_clip = Column(Integer)
    poison2_clip = Column(Integer)
    paralysis1_clip = Column(Integer)
    paralysis2_clip = Column(Integer)
    sleep1_clip = Column(Integer)
    sleep2_clip = Column(Integer)
    exhaust1_clip = Column(Integer)
    exhaust2_clip = Column(Integer)
    flaming_clip = Column(Integer)
    water_clip = Column(Integer)
    freeze_clip = Column(Integer)
    thunder_clip = Column(Integer)
    dragon_clip = Column(Integer)
    slicing_clip = Column(Integer)
    wyvern_clip = Column(Integer)
    demon_clip = Column(Integer)
    armor_clip = Column(Integer)
    tranq_clip = Column(Integer)

class WeaponRecipe(Base):
    __tablename__ = 'weapon_recipe'
    weapon_id = Column(Integer, ForeignKey("weapon.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("item.id"), primary_key=True)
    recipe_type = Column(Text, primary_key=True)
    quantity = Column(Integer)

class Decoration(Base):
    __tablename__ = 'decoration'

    id = Column(Integer, primary_key=True)
    rarity = Column(Integer)

    skilltree_id = Column(Integer, ForeignKey("skilltree.id"))
    slot = Column(Integer)
    icon_color = Column(Text)

    mysterious_feystone_chance = Column(Float)
    glowing_feystone_chance = Column(Float)
    worn_feystone_chance = Column(Float)
    warped_feystone_chance = Column(Float)

    translations = relationship("DecorationText")
    
class DecorationText(Base):
    __tablename__ = 'decoration_text'
    id = Column(Integer, ForeignKey('decoration.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

class Charm(Base):
    __tablename__ = 'charm'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    previous_id = Column(Integer, ForeignKey('charm.id'))
    rarity = Column(Integer)

    skills = relationship('CharmSkill')
    craft_items = relationship('CharmRecipe')
    translations = relationship('CharmText')

class CharmSkill(Base):
    __tablename__ = 'charm_skill'
    charm_id = Column(Integer, ForeignKey('charm.id'), primary_key=True)
    skilltree_id = Column(Integer, ForeignKey('skilltree.id'), primary_key=True)
    level = Column(Integer)

class CharmRecipe(Base):
    __tablename__ = 'charm_recipe'
    charm_id = Column(Integer, ForeignKey("charm.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("item.id"), primary_key=True)
    quantity = Column(Integer)

class CharmText(Base):
    __tablename__ = 'charm_text'
    id = Column(Integer, ForeignKey('charm.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)
    description = Column(Text)
