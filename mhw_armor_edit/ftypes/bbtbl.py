# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class BbtblEntry(Struct):
    STRUCT_SIZE = 6
    close_range: ft.ubyte()
    power: ft.ubyte()
    paralysis: ft.ubyte()
    poison: ft.ubyte()
    sleep: ft.ubyte()
    blast: ft.ubyte()


class Bbtbl(StructFile):
    EntryFactory = BbtblEntry
    MAGIC = 0x01A6
