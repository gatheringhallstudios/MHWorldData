"""
Currently unused. Was added as part of an experiment into identifying kulve weapons
but as it is, currently unused.

Details regarding LBR given by Deathcream. Many thanks.
"""

from mhdata import cfg
from . import structreader as sr

class SafiLbrEntry(sr.AnnotatedStruct):
    """Indices (1 indexed...)
        1-6     1  Attack 
        7-12    2  Defense
        13-18   3  Affinity
        19-24   4  Element
        25-36      Blank
        37-40   5  Slot
        41-46   6  Sharp
        47-60   9  Song Sheet
        61-67   10 Shelling
        68         Blank
        69-70   14 IG Boost
        71-73   15 Normal Capacity
        74         Blank
        75-77   16 Pierce Capacity
        78         Blank
        79-81   17 Spread Capacity
        82         Blank
        83-85   18 Ele Capacity
        86         SA PEP Phials
        87-92   11 Exhaust Phials
        93      12 CB Impact Phials
        94-96   13 Coating Awakens
        97-126   7 Set Bonuses
        127     20 Recoil?
        128     21 Reload?
        129     22 Deviation?
        130-135 23 Status

        # Increase rarity by 4 when mapping to level 2 and beyond.
        136-139 KulveR8Raw
        140-143 KulveR8Ele
        144-147 KulveR7+R6Raw
        148-151 KulveR7+R6Ele
        168-171 KulveR8Status
        172-175 KulveR7+R6Status
    """
    eid: sr.short()
    gs: sr.short()
    sns: sr.short()
    db: sr.short()
    ls: sr.short()
    ham: sr.short()
    hh: sr.short()
    lnc: sr.short()
    gl: sr.short()
    sa: sr.short()
    cb: sr.short()
    ig: sr.short()
    bow: sr.short()
    hbg: sr.short()
    lbg: sr.short()
    unk: sr.int()

    @property
    def values(self):
        return {
            cfg.GREAT_SWORD: self.gs,
            cfg.SWORD_AND_SHIELD: self.sns,
            cfg.DUAL_BLADES: self.db,
            cfg.LONG_SWORD: self.ls,
            cfg.HAMMER: self.ham,
            cfg.HUNTING_HORN: self.hh,
            cfg.LANCE: self.lnc,
            cfg.GUNLANCE: self.gl,
            cfg.SWITCH_AXE: self.sa,
            cfg.CHARGE_BLADE: self.cb,
            cfg.INSECT_GLAIVE: self.ig,
            cfg.BOW: self.bow,
            cfg.HEAVY_BOWGUN: self.hbg,
            cfg.LIGHT_BOWGUN: self.lbg
        }

class SafiLbr(sr.AnnotatedStruct):
    "Limit break entry list for both Safi and Kulve weapons"
    iceborneBytes: sr.int()
    unk: sr.ushort()
    entries: sr.DynamicList(SafiLbrEntry)

class LbEntry(sr.AnnotatedStruct):
    skillId: sr.short()
    upgradeType: sr.int()
    awakenType: sr.uint()
    stars: sr.int()
    hasNext: sr.byte()
    downgradeTarget: sr.short()
    upgradeTarget: sr.short()
    stackable: sr.byte()
    typeExclusive: sr.byte()
    unk1: sr.short()
    unk2: sr.short()
    unk3: sr.short()
    unk4: sr.short()
    unk5: sr.short()
    gs: sr.byte()
    sns: sr.byte()
    db: sr.byte()
    ls: sr.byte()
    ham: sr.byte()
    hh: sr.byte()
    lnc: sr.byte()
    gl: sr.byte()
    sa: sr.byte()
    cb: sr.byte()
    ig: sr.byte()
    bow: sr.byte()
    hbg: sr.byte()
    lbg: sr.byte()
    unk6: sr.int()

class Lb(sr.AnnotatedStruct):
    iceborneBytes: sr.int()
    unk: sr.ushort()
    entries: sr.DynamicList(LbEntry)