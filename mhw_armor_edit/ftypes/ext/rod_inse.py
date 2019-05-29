from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import Struct, StructFile

class RodInseEntry(Struct):
    STRUCT_SIZE = 28
    id: ft.uint()
    attack_type: ft.ubyte() # 0 = Server, 1 = Blunt
    unk1: ft.ubyte() # unknown, could be GMD. Currently the same as id.
    unk2: ft.ubyte() 
    base_model_id: ft.ushort()
    tree_id: ft.byte()
    cost: ft.uint()
    rarity: ft.ubyte()
    power: ft.ushort()
    speed: ft.ushort()
    heal: ft.ushort()
    unk3: ft.ushort()
    dust_type: ft.ushort() # 0 = blast, 1 = heal, 2 = paralysis, 3 = poison
    tree_position: ft.ubyte()
    unk4: ft.ushort() # can't be GMD, as dragonsoul is OOB

class RodInse(StructFile):
    "Kinsect file"
    MAGIC = 0x0109
    EntryFactory = RodInseEntry
