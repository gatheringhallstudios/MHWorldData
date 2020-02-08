# coding: utf-8

from mhw_armor_edit import ftypes  as ft
from mhw_armor_edit.ftypes import StructFile, Struct, short


class ArmUpEntry(Struct):
    STRUCT_SIZE = 22
    unk1: ft.short()
    unk2: ft.short()
    unk3: ft.short()
    unk4: ft.short()
    unk5: ft.short()
    unk6: ft.short()
    unk7: ft.short()
    unk8: ft.short()
    unk9: ft.short()
    unk10: ft.short()
    unk11: ft.short()


class ArmUp(StructFile):
    EntryFactory = ArmUpEntry
    MAGIC = 0x009B
