# coding: utf-8
from enum import Enum
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class ItmFlag(Enum):
    IsDefault = 2 ** 0
    IsQuestOnly = 2 ** 1
    Unknown1 = 2 ** 2
    IsConsumable = 2 ** 3
    IsAppraisal = 2 ** 4
    Unknown2 = 2 ** 5
    IsMega = 2 ** 6
    IsLevelOne = 2 ** 7
    IsLevelTwo = 2 ** 8
    IsLevelThree = 2 ** 9
    IsGlitter = 2 ** 10
    IsDeliverable = 2 ** 11
    IsNotShown = 2 ** 12


class ItmEntry(Struct):
    STRUCT_SIZE = 32
    id: ft.uint()
    sub_type: ft.ubyte()
    type: ft.uint()
    rarity: ft.ubyte()
    carry_limit: ft.ubyte()
    unk_limit: ft.ubyte()
    order: ft.ushort()
    flags: ft.uint()
    icon_id: ft.uint()
    icon_color: ft.ubyte()
    carry_item: ft.ubyte()
    sell_price: ft.uint()
    buy_price: ft.uint()


class Itm(StructFile):
    EntryFactory = ItmEntry
    MAGIC = 0x00AE
