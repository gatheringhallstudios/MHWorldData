# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class WpDatGEntry(Struct):
    STRUCT_SIZE = 68
    id: "<I"
    unk1: "<H"
    base_model_id: "<h"
    part1_id: "<h"
    part2_id: "<h"
    color: "<B"
    tree_id: "<B"
    is_fixed_upgrade: "<B"
    muzzle_type: "<B"
    barrel_type: "<B"
    magazine_type: "<B"
    scope_type: "<B"
    crafting_cost: "<I"
    rarity: "<B"
    raw_damage: "<H"
    defense: "<H"
    affinity: "<b"
    element_id: "<B"
    element_damage: "<H"
    hidden_element_id: "<B"
    hidden_element_damage: "<H"
    elderseal: "<B"
    shell_table_id: "<H"
    deviation: "<B"
    num_gem_slots: "<B"
    gem_slot1_lvl: "<B"
    gem_slot2_lvl: "<B"
    gem_slot3_lvl: "<B"
    unk2: "<I"
    unk3: "<I"
    unk4: "<I"
    unk5: "<B"
    special_ammo_type: "<B"
    tree_position: "<B"
    order: "<H"
    gmd_name_index: "<H"
    gmd_description_index: "<H"
    skill_id: "<H"
    unk6: "<H"


class WpDatG(StructFile):
    EntryFactory = WpDatGEntry
    MAGIC = 0x01B1
