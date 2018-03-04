# Defines SQL objects.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base = declarative_base()

class TextMixin():
    id = Column(Integer, primary_key=True)
    lang_id = Column(String, primary_key=True)

class Monster(Base):
    __tablename__ = 'monster'

    id = Column(Integer, primary_key=True)

class MonsterText(Base, TextMixin):
    __tablename__ = 'monster_text'

    name = Column(String)
    description = Column(String)

class SkillTree(Base):
    __tablename__ = 'skilltree'

    id = Column(Integer, primary_key=True)

class SkillTreeText(Base, TextMixin):
    __tablename__ = 'skilltree_text'

    name = Column(String)
    description = Column(String)

class Skill(Base, TextMixin):
    __tablename__ = 'skill'
    level = Column(Integer, primary_key=True)
    description = Column(String)

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)

class ItemText(Base, TextMixin):
    __tablename__ = "item_text"

    name = Column(String)

class Armor(Base):
    __tablename__ = "armor"

    id = Column(Integer, primary_key=True)
    rarity = Column(Integer)
    part = Column(String) # todo: enum
    male = Column(Boolean)
    female = Column(Boolean)
    slot_1 = Column(Integer)
    slot_2 = Column(Integer)
    slot_3 = Column(Integer)
    defense = Column(Integer)
    fire = Column(Integer)
    water = Column(Integer)
    thunder = Column(Integer)
    ice = Column(Integer)
    dragon = Column(Integer)

class ArmorText(Base, TextMixin):
    __tablename__ = "armor_text"
    
    name = Column(String)

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