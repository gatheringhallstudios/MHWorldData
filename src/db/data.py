# Defines SQL objects.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, Boolean

Base = declarative_base()

class TextMixin():
    id = Column(Integer, primary_key=True)
    lang_id = Column(Text, primary_key=True)

class Monster(Base):
    __tablename__ = 'monster'

    id = Column(Integer, primary_key=True)

class MonsterText(Base, TextMixin):
    __tablename__ = 'monster_text'

    name = Column(Text)
    description = Column(Text)

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
    defense = Column(Integer)
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