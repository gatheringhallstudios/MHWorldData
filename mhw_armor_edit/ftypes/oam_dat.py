# coding: utf-8

from mhw_armor_edit.ftypes import Struct, StructFile


# noinspection PyUnresolvedReferences
class OAmDatEntry(Struct):
    STRUCT_SIZE = 42
    id: "<I"
    set_id: "<H"
    equip_slot: "<B"
    unk1: "<B"
    defense: "<I"
    rarity: "<B"
    list_order: "<H"
    model_id: "<I"
    crafting_cost: "<I"
    variant: "<B"
    unk2: "<B"
    unk3: "<B"
    unk4: "<B"
    fire_res: "<b"
    water_res: "<b"
    ice_res: "<b"
    thunder_res: "<b"
    dragon_res: "<b"
    unk5: "<I"
    set_group: "<H"
    gmd_name_index: "<H"
    gmd_desc_index: "<H"


class OAmDat(StructFile):
    MAGIC = 0x0060
    EntryFactory = OAmDatEntry
