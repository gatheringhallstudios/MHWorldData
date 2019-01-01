# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class WpDatEntry(Struct):
    STRUCT_SIZE = 65
    id: "<I"
    unk1: "<H"
    base_model_id: "<H"
    part1_id: "<H"
    part2_id: "<H"
    color: "<B"
    tree_id: "<B"
    is_fixed_upgrade: "<B"
    crafting_cost: "<I"
    rarity: "<B"
    kire_id: "<B"
    handicraft: "<B"
    raw_damage: "<H"
    defense: "<H"
    affinity: "<b"
    element_id: "<B"
    element_damage: "<H"
    hidden_element_id: "<B"
    hidden_element_damage: "<H"
    elderseal: "<B"
    num_gem_slots: "<B"
    gem_slot1_lvl: "<B"
    gem_slot2_lvl: "<B"
    gem_slot3_lvl: "<B"
    wep1_id: "<H"
    wep2_id: "<H"
    unk2: "<I"
    unk3: "<I"
    unk4: "<I"
    tree_position: "<B"
    order: "<H"
    gmd_name_index: "<H"
    gmd_description_index: "<H"
    skill_id: "<H"
    unk5: "<H"


class WpDat(StructFile):
    EntryFactory = WpDatEntry
    MAGIC = 0x0186
