# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class LbmSkillEntry(Struct):
    STRUCT_SIZE = 10
    unk1: ft.ubyte()
    unk2: ft.ubyte()
    item_id: ft.ushort()
    item_qty: ft.ushort()
    unk3: ft.pad(4)


class LbmSkill(StructFile):
    EntryFactory = LbmSkillEntry
    MAGIC = 0x0046
