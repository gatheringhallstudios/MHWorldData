from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import ext

# note: some code here is from QuestDataDump

class MibHeader(ft.Struct):
    STRUCT_SIZE =  (17 * 4) + (6 * 2) + 3
    mibSignature: ft.ushort()
    padding: ft.uint()
    mibId: ft.uint()
    starRating: ft.ubyte()
    unk1: ft.uint() # Looks to be HR vs LR, in terms of damage modifiers (zorah quests are 6star and LR damage)
    unk2: ft.uint()
    rankRewards: ft.uint() # LR or HR?
    mapId: ft.uint()
    unk4: ft.uint()
    playerSpawn: ft.uint()
    binaryMapToggle: ft.uint()
    dayNightControl: ft.uint()
    weatherControl: ft.uint()
    unk5: ft.uint()
    zennyReward: ft.uint()
    faintPenalty: ft.uint()
    unk6: ft.uint()
    questTimer: ft.uint()
    unk7: ft.ubyte()
    monsterIconId: ext.blist(ft.ushort(), 5)
    hrRestriction: ft.ubyte() # difficulty modifier
    unk8: ft.uint()

class MibObjective(ft.Struct):
    STRUCT_SIZE = 8
    objectiveId: ft.ubyte()
    event: ft.ubyte()
    unk1: ft.ushort()
    objectiveId1: ft.ushort()
    objectiveAmount: ft.ushort()

class MibObjectiveHeader(ft.Struct):
    STRUCT_SIZE = 1
    subobjectivesRequired: ft.ubyte()

class MibObjectiveSection(ft.Struct):
    STRUCT_SIZE = (13 * 4) + 4
    unk1: ft.uint()
    unk2: ft.uint()
    highlightedUnknown2: ft.uint()
    questType: ft.ubyte()
    questTypeIcon: ft.ubyte()
    atFlag: ft.ubyte() # 02 enables AT global modifier
    unk3: ft.ubyte()
    rem_ids: ext.blist(ft.uint(), count=3)
    suppId1: ft.uint()
    unk4: ft.uint() # suppid 2?
    unk5: ft.uint() # suppid 3?
    unk6: ft.uint()
    hrPoints: ft.uint()
    unk7: ft.uint()
    unk8: ft.uint()

class RemFile(ft.Struct):
    STRUCT_SIZE = 110
    signature: ft.uint()
    signatureExt: ft.short()
    id: ft.uint()
    drop_mechanic: ft.uint()
    item_ids: ext.blist(ft.uint(), count=16)
    item_qtys: ext.blist(ft.ubyte(), count=16)
    item_chances: ext.blist(ft.ubyte(), count=16)

    def iter_items(self):
        for i in range(16):
            item_id = self.item_ids[i]
            item_qty = self.item_qtys[i]
            item_chance = self.item_chances[i]
            if item_id and item_qty and item_chance:
                yield (item_id, item_qty, item_chance)