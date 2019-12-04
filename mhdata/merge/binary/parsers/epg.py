from pathlib import Path

from . import structreader as sr

class MappedValue(sr.Readable):
    def __init__(self, base, map):
        self.base = base
        self.map = map

    def read(self, reader: sr.StructReader):
        key = reader.read_struct(self.base)
        return self.map[key]

class EpgBreak(sr.AnnotatedStruct):
    unk1: sr.int()
    unk2: sr.int()
    unk3: sr.int()
    unk4: sr.int()
    unk5: sr.int()

class EpgPart(sr.AnnotatedStruct):
    flinchValue: sr.int()
    unk1: sr.int()
    unk2: sr.int()
    unk3: MappedValue(sr.int(), {
        0: 'red', 1: 'white', 2: 'orange', 3: 'green', 4: '4', 5: '5'
    })
    breaks: sr.DynamicList(EpgBreak)
    unk4: sr.int()
    unk5: sr.int()
    unk6: sr.int()
    unk7: sr.int()

class EpgHitzone(sr.AnnotatedStruct):
    unk0: sr.int()
    Header: sr.int()
    Sever: sr.int()
    Blunt: sr.int()
    Shot: sr.int()
    Fire: sr.int()
    Water: sr.int()
    Ice: sr.int()
    Thunder: sr.int()
    Dragon: sr.int()
    Stun: sr.int()
    unk10: sr.int()

class EpgCleaveZone(sr.AnnotatedStruct):
    damageType: sr.int()
    unkn1: sr.int()
    unkn2: sr.int()
    cleaveHP: sr.int()
    unkn4: sr.int()
    SeverMaybe: sr.byte()
    BluntMaybe: sr.byte()
    ShotMaybe: sr.byte()    

class DttEpg(sr.AnnotatedStruct):
    "Binary type for monster hitzone data"
    filetype: sr.int()
    monster_id: sr.uint()
    section: sr.int()
    baseHP: sr.int()
    parts: sr.DynamicList(EpgPart)
    hitzones: sr.DynamicList(EpgHitzone)
    cleaves: sr.DynamicList(EpgCleaveZone)

def load_epg(filepath):
    filepath = Path(filepath)
    data = open(filepath,'rb').read()
    return sr.StructReader(data).read_struct(DttEpg)