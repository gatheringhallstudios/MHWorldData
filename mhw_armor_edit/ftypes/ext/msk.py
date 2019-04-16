from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import Struct, StructFile

class MskEntry(Struct):
    STRUCT_SIZE = 20
    id: ft.uint()
    note1: ft.uint() # note: any notes at FF FF FF FF means that it doesn't exist
    note2: ft.uint()
    note3: ft.uint()
    note4: ft.uint()

class Msk(StructFile):
    "Hunting Horn melody file"
    MAGIC = 0x0146
    EntryFactory = MskEntry
