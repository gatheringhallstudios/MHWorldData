# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class WepGlanEntry(Struct):
    STRUCT_SIZE = 8
    id: "<I"
    type: "<H"
    level: "<H"


class WepGlan(StructFile):
    EntryFactory = WepGlanEntry
    MAGIC = 0x0177
