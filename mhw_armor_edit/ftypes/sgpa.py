# coding: utf-8

from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class SgpaEntry(Struct):
    STRUCT_SIZE = 28
    id: ft.uint()
    order: ft.uint()
    size: ft.uint()
    skill1_id: ft.uint()
    skill1_incr: ft.uint()
    skill2_id: ft.uint()
    skill2_incr: ft.uint()


class Sgpa(StructFile):
    EntryFactory = SgpaEntry
    MAGIC = 0x00BC
