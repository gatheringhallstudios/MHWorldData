# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class LbmBaseEntry(Struct):
    STRUCT_SIZE = 14
    rarity: ft.ubyte()
    equip_type: ft.ubyte()
    crafting_cost: ft.uint()
    item1_id: ft.ushort()
    item1_qty: ft.ushort()
    item2_id: ft.ushort()
    item2_qty: ft.ushort()


class LbmBase(StructFile):
    EntryFactory = LbmBaseEntry
    MAGIC = 0x0046
