# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class SgpaEntry(Struct):
    STRUCT_SIZE = 28
    id: "<I"
    order: "<I"
    size: "<I"
    skill1_id: "<I"
    skill1_incr: "<I"
    skill2_id: "<I"
    skill2_incr: "<I"


class Sgpa(StructFile):
    EntryFactory = SgpaEntry
    MAGIC = 0x00AE
