# coding: utf-8

from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class WpDatGEntry(Struct):
    STRUCT_SIZE = 69
    id: ft.uint()
    unk1: ft.ushort()
    base_model_id: ft.short()
    part1_id: ft.short()
    part2_id: ft.short()
    unk7: ft.ubyte()
    color: ft.ubyte()
    tree_id: ft.ubyte()
    is_fixed_upgrade: ft.ubyte()
    muzzle_type: ft.ubyte()
    barrel_type: ft.ubyte()
    magazine_type: ft.ubyte()
    scope_type: ft.ubyte()
    crafting_cost: ft.uint()
    rarity: ft.ubyte()
    raw_damage: ft.ushort()
    defense: ft.ushort()
    affinity: ft.byte()
    element_id: ft.ubyte()
    element_damage: ft.ushort()
    hidden_element_id: ft.ubyte()
    hidden_element_damage: ft.ushort()
    elderseal: ft.ubyte()
    shell_table_id: ft.ushort()
    deviation: ft.ubyte()
    num_gem_slots: ft.ubyte()
    gem_slot1_lvl: ft.ubyte()
    gem_slot2_lvl: ft.ubyte()
    gem_slot3_lvl: ft.ubyte()
    unk2: ft.uint()
    unk3: ft.uint()
    unk4: ft.uint()
    unk5: ft.ubyte()
    special_ammo_type: ft.ubyte()
    tree_position: ft.ubyte()
    order: ft.ushort()
    gmd_name_index: ft.ushort()
    gmd_description_index: ft.ushort()
    skill_id: ft.ushort()
    unk6: ft.ushort()


class WpDatG(StructFile):
    EntryFactory = WpDatGEntry
    MAGIC = 0x021D
