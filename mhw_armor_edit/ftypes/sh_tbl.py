# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


def ammo(name):
    return (
        (f"{name}_capacity", "<B"),
        (f"{name}_recoil", "<B"),
        (f"{name}_reload", "<B"),
    )


class ShlTblEntry(Struct):
    STRUCT_SIZE = 111
    STRUCT_FIELDS = (
        ammo("normal1")
        + ammo("normal2")
        + ammo("normal3")
        + ammo("pierce1")
        + ammo("pierce2")
        + ammo("pierce3")
        + ammo("spread1")
        + ammo("spread2")
        + ammo("spread3")
        + ammo("cluster1")
        + ammo("cluster2")
        + ammo("cluster3")
        + ammo("wyvern")
        + ammo("sticky1")
        + ammo("sticky2")
        + ammo("sticky3")
        + ammo("slicing")
        + ammo("flaming")
        + ammo("water")
        + ammo("freeze")
        + ammo("thunder")
        + ammo("dragon")
        + ammo("poison1")
        + ammo("poison2")
        + ammo("paralysis1")
        + ammo("paralysis2")
        + ammo("sleep1")
        + ammo("sleep2")
        + ammo("exhaust1")
        + ammo("exhaust2")
        + ammo("recover1")
        + ammo("recover2")
        + ammo("demon")
        + ammo("armor")
        + ammo("unknown1")
        + ammo("unknown2")
        + ammo("tranq")
    )


class ShlTbl(StructFile):
    EntryFactory = ShlTblEntry
    MAGIC = 0x01A6
