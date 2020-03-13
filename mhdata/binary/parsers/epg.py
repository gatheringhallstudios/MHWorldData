from pathlib import Path

from . import structreader as sr
from .decrypt import CapcomBlowfish

class MappedValue(sr.Readable):
    def __init__(self, base, map):
        self.base = base
        self.map = map

    def read(self, reader: sr.StructReader):
        key = reader.read_struct(self.base)
        try:
            return self.map[key]
        except KeyError:
            valid = ", ".join(str(k) for k in self.map.keys())
            raise KeyError(f"Key {key} is not in MappedValue, valid keys are {valid}")

class EpgSubpart(sr.AnnotatedStruct):
    hzv_base: sr.int()
    hzv_broken: sr.int()

    "White spike Nergi / Molten Kulve"
    hzv_special1: sr.int() 

    "Black spike Nergi"
    hzv_special2: sr.int()

    "Gloss black spike Nergi"
    hzv_special3: sr.int()

class EpgSubpartCombined(sr.AnnotatedStruct):
    sub_base: EpgSubpart()
    sub_unknown: EpgSubpart()

class EpgPart(sr.AnnotatedStruct):
    flinchValue: sr.int()
    cleave1: sr.int()
    cleave2: sr.int()
    cleave3: sr.int()
    extract: MappedValue(sr.int(), {
        0: 'red', 1: 'white', 2: 'orange', 3: 'green', 4: '4', 5: '5'
    })
    subparts: sr.DynamicList(EpgSubpartCombined)
    unk4: sr.int()
    unk5: sr.int()
    unk6: sr.int()
    unk7: sr.short()

    def iter_cleaves(self):
        yield self.cleave1
        yield self.cleave2
        yield self.cleave3

class EpgHitzone(sr.AnnotatedStruct):
    timer: sr.float()
    sever: sr.int()
    blunt: sr.int()
    shot: sr.int()
    fire: sr.int()
    water: sr.int()
    ice: sr.int()
    thunder: sr.int()
    dragon: sr.int()
    stun: sr.int()
    mount: sr.int()

class EpgCleaveZone(sr.AnnotatedStruct):
    damage_type: MappedValue(sr.int(), {
        0: 'any', 1: 'sever', 2: 'blunt', 3: 'shot'
    })
    unkn1: sr.int()
    unkn2: sr.int()
    special_hp: sr.int()
    unkn4: sr.int() # all tails use 1 (but do all severables?)

    # 0 makes kulve horns affected by part breaker. Nergi 1 requires spikes to be cut
    special_unk: sr.byte()

    BluntMaybe: sr.byte()
    ShotMaybe: sr.byte()    

class DttEpg(sr.AnnotatedStruct):
    "Binary type for monster hitzone data"
    iceborneBytes: sr.int()
    filetype: sr.int()
    monster_id: sr.uint()
    section: sr.int()
    baseHP: sr.int()
    parts: sr.DynamicList(EpgPart)
    hitzones: sr.DynamicList(EpgHitzone)
    cleaves: sr.DynamicList(EpgCleaveZone)

EPG_KEY = b"sJV4g7d55gKnQB5nS6XJ9pZ1qZmmQwNnSbidUW1OeAhHrpPd6MKbfsrt"

def load_epg(filepath):
    filepath = Path(filepath)
    data = CapcomBlowfish(open(filepath,'rb').read(), EPG_KEY)
    return sr.StructReader(data).read_struct(DttEpg)