# Defines SQL objects.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, Float, Text, Boolean
from sqlalchemy.orm import relationship

Base = declarative_base()

class Language(Base):
    __tablename__ = 'language'
    id = Column(Text, primary_key=True)
    name = Column(Text)
    is_complete = Column(Text)

class Location(Base):
    __tablename__ = 'location_text'
    id = Column(Integer, primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

class Monster(Base):
    __tablename__ = 'monster'

    id = Column(Integer, primary_key=True)
    size = Column(Text)

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

    has_alt_weakness = Column(Boolean, default=False)
    alt_weakness_fire = Column(Integer)
    alt_weakness_water = Column(Integer)
    alt_weakness_ice = Column(Integer)
    alt_weakness_thunder = Column(Integer)
    alt_weakness_dragon = Column(Integer)

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
    description = Column(Text)
    alt_state_description = Column(Text)

class MonsterHitzone(Base):
    __tablename__ = 'monster_hitzone'

    monster_id = Column(Integer, ForeignKey('monster.id'), primary_key=True)
    part_id = Column(Integer, ForeignKey('monster_part_text.id'), primary_key=True)

    cut = Column(Integer)
    impact = Column(Integer)
    shot = Column(Integer)
    fire = Column(Integer)
    water = Column(Integer)
    ice = Column(Integer)
    thunder = Column(Integer)
    dragon = Column(Integer)
    ko = Column(Integer)
    
    body_part_translations = relationship("MonsterPartText", uselist=True)

class MonsterBreak(Base):
    __tablename__ = 'monster_break'

    monster_id = Column(Integer, ForeignKey('monster.id'), primary_key=True)
    part_id = Column(Integer, ForeignKey('monster_part_text.id'), primary_key=True)

    flinch = Column(Integer)
    wound = Column(Integer)
    sever = Column(Integer)
    extract = Column(Text)

    body_part_translations = relationship("MonsterPartText", uselist=True)

class MonsterPartText(Base):
    __tablename__ = 'monster_part_text'
    # todo: is it ok to have no monster id?
    # currently it doesn't to allow us to add an optimization step for "exact matching part names"
    id = Column(Integer, primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

class MonsterReward(Base):
    __tablename__ = 'monster_reward'
 
    # note: it is possible for there to be multiple entries of the same thing.
    # therefore, this join-table has no "real id" and uses a surrogate instead

    id = Column(Integer, primary_key=True, autoincrement=True)

    monster_id = Column(Integer, ForeignKey('monster.id'))
    condition_id = Column(Integer, ForeignKey('monster_reward_condition_text.id'))
    
    rank = Column(Text)
    item_id = Column(Integer, ForeignKey('item.id'))
    
    stack_size = Column(Integer)
    percentage = Column(Integer)
    
    condition_translations = relationship("MonsterRewardConditionText", uselist=True)

class MonsterRewardConditionText(Base):
    __tablename__ = 'monster_reward_condition_text'
    # todo: is it ok to have no monster id?
    # currently it doesn't to allow us to add an optimization step for "exact matching part names"
    id = Column(Integer, primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)


class MonsterHabitat(Base):
    __tablename__ = 'monster_habitat'
    monster_id = Column(Integer, ForeignKey('monster.id'), primary_key=True)
    location_id = Column(Integer, ForeignKey('location_text.id'), primary_key=True)
    start_area = Column(Text)
    move_area = Column(Text)
    rest_area = Column(Text)

class SkillTree(Base):
    __tablename__ = 'skilltree'

    id = Column(Integer, primary_key=True)

    translations = relationship("SkillTreeText")
    skills = relationship("Skill")
    # todo: decide the relationship to skill, and whether skill should be skill_text

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

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    rarity = Column(Integer)

    buy_price = Column(Integer)
    sell_price = Column(Integer)
    carry_limit = Column(Integer)

    translations = relationship("ItemText")

class ItemText(Base):
    __tablename__ = "item_text"
    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)
    description = Column(Text)

class ArmorSet(Base):
    __tablename__ = "armorset"
    id = Column(Integer, primary_key=True)
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
    id = Column(Integer, primary_key=True)
    skilltree_id = Column(Integer, ForeignKey('skilltree.id'), primary_key=True)
    requirement = Column(Integer)

class Armor(Base):
    __tablename__ = "armor"

    id = Column(Integer, primary_key=True)
    rarity = Column(Integer)
    armor_type = Column(Text)
    armorset_id = Column(Integer, ForeignKey("armorset.id"))

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
    slot_1 = Column(Integer)
    slot_2 = Column(Integer)
    slot_3 = Column(Integer)

    element_type = Column(Text)
    element_damage = Column(Integer)
    element_hidden = Column(Boolean)

    # todo: sharpness, once we decide how we're storing it

    previous_weapon_id = Column(ForeignKey("weapon.id"), nullable=True)
    craftable = Column(Boolean, default=False)
    final = Column(Boolean, default=False)

    glaive_boost_type = Column(Text)
    deviation = Column(Text)
    special_ammo = Column(Text)

    ammo_normal_1 = Column(Integer)
    ammo_normal_2 = Column(Integer)
    ammo_normal_3 = Column(Integer)
    ammo_pierce_1 = Column(Integer)
    ammo_pierce_2 = Column(Integer)
    ammo_pierce_3 = Column(Integer)
    ammo_spread_1 = Column(Integer)
    ammo_spread_2 = Column(Integer)
    ammo_spread_3 = Column(Integer)
    ammo_sticky_1 = Column(Integer)
    ammo_sticky_2 = Column(Integer)
    ammo_sticky_3 = Column(Integer)
    ammo_cluster_1 = Column(Integer)
    ammo_cluster_2 = Column(Integer)
    ammo_cluster_3 = Column(Integer)
    ammo_recover_1 = Column(Integer)
    ammo_recover_2 = Column(Integer)
    ammo_sleep_1 = Column(Integer)
    ammo_sleep_2 = Column(Integer)
    ammo_exhaust_1 = Column(Integer)
    ammo_exhaust_2 = Column(Integer)
    ammo_flaming = Column(Integer)
    ammo_water = Column(Integer)
    ammo_freeze = Column(Integer)
    ammo_thunder = Column(Integer)
    ammo_dragon = Column(Integer)
    ammo_slicing = Column(Integer)
    ammo_wyvern = Column(Integer)
    ammo_demon = Column(Integer)
    ammo_armor = Column(Integer)
    ammo_tranq = Column(Integer)

    translations = relationship("WeaponText")

    # TODO: Find a way to create two relationships: one to craft, one to upgrade.
    # the above will require more sqlalchemy knowledge that unfortunately I don't have.

class WeaponText(Base):
    __tablename__ = "weapon_text"
    id = Column(Integer, ForeignKey('weapon.id'), primary_key=True)
    lang_id = Column(Text, ForeignKey('language.id'), primary_key=True)
    name = Column(Text)

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
