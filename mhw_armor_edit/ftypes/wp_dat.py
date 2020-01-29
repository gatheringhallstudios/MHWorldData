# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class WpDatEntry(Struct):
    STRUCT_SIZE = 66
    id: ft.uint()
    unk1: ft.ubyte()
    unk6: ft.ubyte()
    base_model_id: ft.ushort()
    part1_id: ft.ushort()
    part2_id: ft.ushort()
    unk7: ft.ubyte()
    color: ft.ubyte()
    tree_id: ft.ubyte()
    is_fixed_upgrade: ft.ubyte()
    crafting_cost: ft.uint()
    rarity: ft.ubyte()
    kire_id: ft.ubyte()
    handicraft: ft.ubyte()
    raw_damage: ft.ushort()
    defense: ft.ushort()
    affinity: ft.byte()
    element_id: ft.ubyte()
    element_damage: ft.ushort()
    hidden_element_id: ft.ubyte()
    hidden_element_damage: ft.ushort()
    elderseal: ft.ubyte()
    num_gem_slots: ft.ubyte()
    gem_slot1_lvl: ft.ubyte()
    gem_slot2_lvl: ft.ubyte()
    gem_slot3_lvl: ft.ubyte()
    wep1_id: ft.ushort()
    wep2_id: ft.ushort()
    unk2: ft.uint()
    unk3: ft.uint()
    unk4: ft.uint()
    tree_position: ft.ubyte()
    order: ft.ushort()
    gmd_name_index: ft.ushort()
    gmd_description_index: ft.ushort()
    skill_id: ft.ushort()
    unk5: ft.ushort()


class WpDat(StructFile):
    EntryFactory = WpDatEntry
    MAGIC = 0x01C1
