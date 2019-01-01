# coding: utf-8

from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class SklPtDatEntry(Struct):
    STRUCT_SIZE = 2
    is_set_bonus: ft.ubyte()
    unk1: ft.ubyte()


class SklPtDat(StructFile):
    EntryFactory = SklPtDatEntry
    MAGIC = 0x005E
