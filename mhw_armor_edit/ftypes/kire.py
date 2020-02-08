# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class KireEntry(Struct):
    STRUCT_SIZE = 18
    id: ft.uint()
    red: ft.ushort()
    orange: ft.ushort()
    yellow: ft.ushort()
    green: ft.ushort()
    blue: ft.ushort()
    white: ft.ushort()
    purple: ft.ushort()


class Kire(StructFile):
    EntryFactory = KireEntry
    MAGIC = 0x01C1
