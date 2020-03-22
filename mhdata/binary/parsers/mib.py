from typing import Iterable
from pathlib import Path

from . import structreader as sr
from .decrypt import CapcomBlowfish

# note: some code here is from QuestDataDump

class MibHeader(sr.AnnotatedStruct):
    mibSignature: sr.ulong()
    padding: sr.ushort()
    mibId: sr.uint()
    starRating: sr.ubyte() # 0 is invisible
    unk1: sr.uint() # Looks to be HR vs LR, in terms of damage modifiers (zorah quests are 6star and LR damage)
    unk2: sr.uint()
    rank: sr.uint() # LR or HR?
    mapId: sr.uint()
    playerSpawn: sr.MappedValue(sr.uint(), {
        0: 'camp1', 1: 'chooseRNG', 2: 'choose'
    })
    fixedSpawn: sr.uint()
    binaryMapToggle: sr.uint() # 0 off 2 on
    dayNightControl: sr.MappedValue(sr.uint(), {
        0: 'gametime',
        1: 'latenight',
        2: 'dawn',
        3: 'earlyday',
        4: 'noon',
        5: 'lateday',
        6: 'dusk',
        7: 'earlynight',
        8: 'midnight',
        9: 'pause'
    }, warn=True)
    weatherControl: sr.MappedValue(sr.uint(), {
        0: 'random',
        1: 'disable',
        2: 'alt1',
        3: 'alt2',
        4: 'alt3',
        5: 'alt4',
    }, warn=True)
    unk5: sr.uint()
    zennyReward: sr.uint()
    faintPenalty: sr.uint()
    zennySubReward: sr.uint()
    questTimer: sr.uint()
    unk7: sr.ubyte()
    monsterIconId: sr.blist(sr.ushort(), 5)
    hrRestriction: sr.ubyte() # difficulty modifier
    unk8: sr.uint()

class MibObjective(sr.AnnotatedStruct):
    STRUCT_SIZE = 8
    objective_type: sr.ubyte()
    event: sr.ubyte()
    unk1: sr.ushort()
    objective_id: sr.ushort()
    objective_amount: sr.ushort()

class MibObjectiveSection(sr.AnnotatedStruct):
    objectives: sr.blist(MibObjective(), 2)
    objectives_req: sr.ubyte()
    sub_objectives: sr.blist(MibObjective(), 2)
        
    unk1: sr.uint()
    unk2: sr.uint()
    highlightedUnknown2: sr.uint()

    quest_type: sr.ubyte()

    quest_type_icon: sr.ubyte()
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

class MibMonster(sr.AnnotatedStruct):
    monster_id: sr.int()
    spawn_id: sr.uint()
    unk1: sr.int()
    tempered: sr.byte()
    health: sr.int()
    damage: sr.int()
    player_damage: sr.int()
    health_damage_variance: sr.int()
    size: sr.int()
    size_variation: sr.int()
    unk2: sr.int()
    partHP: sr.int()
    status_base: sr.int()
    status_build_up: sr.int()
    stun: sr.int()
    exhaust: sr.int()
    mount: sr.int()

class RemFile(sr.AnnotatedStruct):
    STRUCT_SIZE = 110
    ibBytes: sr.uint()
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
    objective: MibObjectiveSection()
    monsters: sr.blist(MibMonster(), 7)

QUEST_KEY = b"TZNgJfzyD2WKiuV4SglmI6oN5jP2hhRJcBwzUooyfIUTM4ptDYGjuRTP"

def load_quest(filepath) -> Mib:
    filepath = Path(filepath)
    data = CapcomBlowfish(open(filepath,'rb').read(), QUEST_KEY)
    return sr.read_struct(data, Mib)

