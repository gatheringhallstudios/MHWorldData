# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import Struct, StructFile


class AmDatEntry(Struct):
    STRUCT_SIZE = 60
    id: ft.uint()
    order: ft.ushort()
    variant: ft.ubyte()
    set_id: ft.ushort()
    type: ft.ubyte()
    equip_slot: ft.ubyte()
    defense: ft.ushort()
    mdl_main_id: ft.ushort()
    mdl_secondary_id: ft.ushort()
    icon_color: ft.ubyte()
    pad8: ft.ubyte()
    icon_effect: ft.ubyte()
    rarity: ft.ubyte()
    cost: ft.uint()
    fire_res: ft.byte()
    water_res: ft.byte()
    ice_res: ft.byte()
    thunder_res: ft.byte()
    dragon_res: ft.byte()
    num_gem_slots: ft.ubyte()
    gem_slot1_lvl: ft.ubyte()
    gem_slot2_lvl: ft.ubyte()
    gem_slot3_lvl: ft.ubyte()
    set_skill1: ft.short()
    set_skill1_lvl: ft.ubyte()
    set_skill2: ft.short()
    set_skill2_lvl: ft.ubyte()
    skill1: ft.short()
    skill1_lvl: ft.ubyte()
    skill2: ft.short()
    skill2_lvl: ft.ubyte()
    skill3: ft.short()
    skill3_lvl: ft.ubyte()
    gender: ft.ubyte()
    pad11: ft.ubyte()
    pad12: ft.ubyte()
    pad13: ft.ubyte()
    set_group: ft.ushort()
    gmd_name_index: ft.ushort()
    gmd_desc_index: ft.ushort()
    is_permanent: ft.ubyte()


class AmDat(StructFile):
    MAGIC = 0x005d
    EntryFactory = AmDatEntry
