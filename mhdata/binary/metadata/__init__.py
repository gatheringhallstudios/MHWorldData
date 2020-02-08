"""
Module that handles the loading of pre-configured metadata.
Some data cannot be determined from game files or source data, and needs additional information to gather.

Some of the data here comes from the QuestDataDump project.
"""

from .location_meta import load_area_map
from .monster_metadata import MonsterMetadata, MonsterMetaEntry