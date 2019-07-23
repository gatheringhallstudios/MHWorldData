from typing import Iterable
from pathlib import Path
from Crypto.Cipher import Blowfish

from .bcore import load_schema, load_text, get_chunk_root

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

class QuestInfo:
    "An encapsulation of quest binary data and referenced cross data"
    def __init__(self, name, header: MibHeader, objective: MibObjectiveSection, reward_data_list):
        self.name = name
        self.header = header
        self.objective = objective
        self.reward_data_list = reward_data_list

def load_quests() -> Iterable[QuestInfo]:
    quests = []
    quest_base_path = Path(get_chunk_root()).joinpath('quest')
    rem_base_path = quest_base_path.joinpath('rem')

    quest_files = quest_base_path.rglob("*.mib")

    for path in quest_files:
        data = CapcomBlowfish(open(path,'rb').read())

        quest_text_fname = path.stem.replace('questData_', 'q')
        quest_text = load_text(f'common/text/quest/{quest_text_fname}')

        name = quest_text[0]

        # todo: disable this line if we wanna find out other ways to mark something as invalid
        if name['en'] in ('Unavailable', 'Invalid Message'):
            continue

        offset = 0
        header = MibHeader(None, 0, data, offset=offset)
        offset += MibHeader.STRUCT_SIZE

        objectives = []
        for i in range(2):
            obj = MibObjective(None, 0, data, offset=offset)
            offset += MibObjective.STRUCT_SIZE
            objectives.append(obj)

        objective_header = MibObjectiveHeader(None, 0, data, offset=offset)
        offset += MibObjectiveHeader.STRUCT_SIZE

        sub_objectives = []
        for i in range(2):
            obj = MibObjective(None, 0, data, offset=offset)
            offset += MibObjective.STRUCT_SIZE
            sub_objectives.append(obj)

        objective = MibObjectiveSection(None, 0, data, offset=offset)
        offset += MibObjectiveSection.STRUCT_SIZE

        # Load REMS (reward files)
        rem_files = [rem_base_path.joinpath(f'remData_{rem_id}.rem') for rem_id in objective.rem_ids]
        rem_files = filter(lambda r: r.exists(), rem_files)
        rem_files = [RemFile(None, 0, open(path,'rb').read(), offset=0) for path in rem_files]

        quest = QuestInfo(name, header, objective, rem_files)
        quests.append(quest)

    return quests

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def CapcomBlowfish(file):
    cipher = Blowfish.new(b"TZNgJfzyD2WKiuV4SglmI6oN5jP2hhRJcBwzUooyfIUTM4ptDYGjuRTP", Blowfish.MODE_ECB)
    return endianness_reversal(cipher.decrypt(endianness_reversal(file)))
