# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class WepWslEntry(Struct):
    STRUCT_SIZE = 7
    id: "<I"
    note1: "<B"
    note2: "<B"
    note3: "<B"


class WepWsl(StructFile):
    EntryFactory = WepWslEntry
    MAGIC = 0x0177
