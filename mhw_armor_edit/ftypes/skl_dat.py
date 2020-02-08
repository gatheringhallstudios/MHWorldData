# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class SklDatEntry(Struct):
    STRUCT_SIZE = 11
    skill_id: "<H"
    level: "<B"
    param1: "<H"
    param2: "<H"
    param3: "<H"
    param4: "<H"


class SklDat(StructFile):
    EntryFactory = SklDatEntry
    MAGIC = 0x0087
