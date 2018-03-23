# Defines SQL objects.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, Text, Boolean

Base = declarative_base()

class TextMixin():
    id = Column(Integer, primary_key=True)
    lang_id = Column(Text, primary_key=True)

class Monster(Base):
    __tablename__ = 'monster'

    id = Column(Integer, primary_key=True)
    size = Column(Text)

class MonsterText(Base, TextMixin):
    __tablename__ = 'monster_text'

    name = Column(Text)
    description = Column(Text)

class MonsterHitzone(Base):
    __tablename__ = 'monster_hitzone'

    monster_id = Column(Integer, ForeignKey('monster.id'), primary_key=True)
    body_part = Column(Text, primary_key=True)

    cut = Column(Integer)
    impact = Column(Integer)
    shot = Column(Integer)
    fire = Column(Integer)
    water = Column(Integer)
    ice = Column(Integer)
    thunder = Column(Integer)
    dragon = Column(Integer)
    ko = Column(Integer)

class MonsterReward(Base):
    __tablename__ = 'monster_reward'
 
    # note: it is possible for there to be multiple entries.
    # therefore, this join-table has no real primary key.
    id = Column(Integer, primary_key=True)

    monster_id = Column(Integer, ForeignKey('monster.id'))
    condition = Column(Text)
    rank = Column(Text)
    item_id = Column(Integer, ForeignKey('item.id'))
    
    stack_size = Column(Integer)
    percentage = Column(Integer)

class SkillTree(Base):
    __tablename__ = 'skilltree'

    id = Column(Integer, primary_key=True)

class SkillTreeText(Base, TextMixin):
    __tablename__ = 'skilltree_text'

    name = Column(Text)
    description = Column(Text)

class Skill(Base):
    __tablename__ = 'skill'
    skilltree_id = Column(Integer, primary_key=True)
    lang_id = Column(Text, primary_key=True)
    level = Column(Integer, primary_key=True)
    description = Column(Text)

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)

class ItemText(Base, TextMixin):
    __tablename__ = "item_text"

    name = Column(Text)

class Armor(Base):
    __tablename__ = "armor"

    id = Column(Integer, primary_key=True)
    rarity = Column(Integer)
    armor_type = Column(Text)
    armorset_id = Column(Integer)

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

class ArmorText(Base, TextMixin):
    __tablename__ = "armor_text"
    
    name = Column(Text)

class ArmorSet(Base, TextMixin):
    __tablename__ = "armorset_text"

    name = Column(Text)

class ArmorSkill(Base):
    __tablename__ = 'armor_skill'
    armor_id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, primary_key=True)
    level = Column(Integer)

class ArmorRecipe(Base):
    __tablename__ = 'armor_recipe'
    armor_id = Column(Integer, primary_key=True)
    item_id = Column(Integer, primary_key=True)
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

    glaive_boost_type = Column(Text)
    deviation = Column(Text)
    special_ammo = Column(Text)

    previous_weapon = Column(ForeignKey("weapon.id"), nullable=True)
    
    craftable = Column(Boolean, default=False)
    final = Column(Boolean, default=False)

class WeaponText(Base, TextMixin):
    __tablename__ = "weapon_text"

    name = Column(Text)

class WeaponRecipe(Base):
    __tablename__ = 'weapon_recipe'
    weapon_id = Column(Integer, ForeignKey("weapon.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("item.id"), primary_key=True)
    recipe_type = Column(Text, primary_key=True)
    quantity = Column(Integer)

