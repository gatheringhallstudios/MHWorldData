# coding: utf-8

from mhw_armor_edit import ftypes  as ft
from mhw_armor_edit.ftypes import StructFile, Struct, uint


class AmrsEntry(Struct):
    STRUCT_SIZE = 4
    id: ft.uint()


class Amrs(StructFile):
    EntryFactory = AmrsEntry
    MAGIC = 0x000C
