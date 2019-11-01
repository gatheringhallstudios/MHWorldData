from typing import Iterable
from pathlib import Path
from Crypto.Cipher import Blowfish

from .structreader import StructReader
from . import structreader as sr

from ...binary.load import load_text

# note: some code here is from QuestDataDump

class MibHeader(sr.AnnotatedStruct):
    STRUCT_SIZE =  (17 * 4) + (6 * 2) + 3
    mibSignature: sr.ushort()
    padding: sr.uint()
    mibId: sr.uint()
    starRating: sr.ubyte()
    unk1: sr.uint() # Looks to be HR vs LR, in terms of damage modifiers (zorah quests are 6star and LR damage)
    unk2: sr.uint()
    rankRewards: sr.uint() # LR or HR?
    mapId: sr.uint()
    unk4: sr.uint()
    playerSpawn: sr.uint()
    binaryMapToggle: sr.uint()
    dayNightControl: sr.uint()
    weatherControl: sr.uint()
    unk5: sr.uint()
    zennyReward: sr.uint()
    faintPenalty: sr.uint()
    unk6: sr.uint()
    questTimer: sr.uint()
    unk7: sr.ubyte()
    monsterIconId: sr.blist(sr.ushort(), 5)
    hrRestriction: sr.ubyte() # difficulty modifier
    unk8: sr.uint()

class MibObjective(sr.AnnotatedStruct):
    STRUCT_SIZE = 8
    objectiveId: sr.ubyte()
    event: sr.ubyte()
    unk1: sr.ushort()
    objectiveId1: sr.ushort()
    objectiveAmount: sr.ushort()

class MibObjectiveHeader(sr.AnnotatedStruct):
    STRUCT_SIZE = 1
    subobjectivesRequired: sr.ubyte()

class MibObjectiveSection(sr.AnnotatedStruct):
    STRUCT_SIZE = (13 * 4) + 4
    unk1: sr.uint()
    unk2: sr.uint()
    highlightedUnknown2: sr.uint()
    questType: sr.ubyte()
    questTypeIcon: sr.ubyte()
    atFlag: sr.ubyte() # 02 enables AT global modifier
    unk3: sr.ubyte()
    rem_ids: sr.blist(sr.uint(), count=3)
    suppId1: sr.uint()
    unk4: sr.uint() # suppid 2?
    unk5: sr.uint() # suppid 3?
    unk6: sr.uint()
    hrPoints: sr.uint()
    unk7: sr.uint()
    unk8: sr.uint()

class RemFile(sr.AnnotatedStruct):
    STRUCT_SIZE = 110
    signature: sr.uint()
    signatureExt: sr.short()
    id: sr.uint()
    drop_mechanic: sr.uint()
    item_ids: sr.blist(sr.uint(), count=16)
    item_qtys: sr.blist(sr.ubyte(), count=16)
    item_chances: sr.blist(sr.ubyte(), count=16)

    def iter_items(self):
        for i in range(16):
            item_id = self.item_ids[i]
            item_qty = self.item_qtys[i]
            item_chance = self.item_chances[i]
            if item_id and item_qty and item_chance:
                yield (item_id, item_qty, item_chance)

class Mib(sr.AnnotatedStruct):
    header: MibHeader()
    objectives: sr.blist(MibObjective(), 2)
    objective_header: MibObjectiveHeader()
    sub_objectives: sr.blist(MibObjective(), 2)
    objective_section: MibObjectiveSection()

def load_quest(filepath) -> Mib:
    filepath = Path(filepath)
    data = CapcomBlowfish(open(filepath,'rb').read())
    return StructReader(data).read_struct(Mib)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def CapcomBlowfish(file):
    cipher = Blowfish.new(b"TZNgJfzyD2WKiuV4SglmI6oN5jP2hhRJcBwzUooyfIUTM4ptDYGjuRTP", Blowfish.MODE_ECB)
    return endianness_reversal(cipher.decrypt(endianness_reversal(file)))
