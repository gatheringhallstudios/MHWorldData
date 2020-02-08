# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class EqCrtEntry(Struct):
    STRUCT_SIZE = 37
    equip_type: ft.ubyte()
    equip_id: ft.ushort()
    key_item: ft.ushort()
    unk1: ft.int()
    unk2: ft.uint()
    rank: ft.uint()
    unk3: ft.pad(4)
    item1_id: ft.ushort()
    item1_qty: ft.ubyte()
    item2_id: ft.ushort()
    item2_qty: ft.ubyte()
    item3_id: ft.ushort()
    item3_qty: ft.ubyte()
    item4_id: ft.ushort()
    item4_qty: ft.ubyte()
    unk4: ft.pad(4)


class EqCrt(StructFile):
    EntryFactory = EqCrtEntry
    MAGIC = 0x0079
