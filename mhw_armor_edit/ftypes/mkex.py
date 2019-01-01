# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class MkexEntry(Struct):
    STRUCT_SIZE = 176
    STRUCT_FIELDS = (
        ("source_item_id", "<I"),
        ("int2", "<I"),
    ) + tuple(
        (f"f{i}", "<H")
        for i in range(84)
    )


class Mkex(StructFile):
    EntryFactory = MkexEntry
    MAGIC = 0x00B4
