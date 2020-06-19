"""
Currently unused. Was added as part of an experiment into identifying kulve weapons
but as it is, currently unused.
"""

from . import structreader as sr

class LbrEntry(sr.AnnotatedStruct):
    eid: sr.short()
    gs: sr.short()
    sns: sr.short()
    db: sr.short()
    ls: sr.short()
    ham: sr.short()
    hh: sr.byte()
    lnc: sr.short()
    gl: sr.short()
    sa: sr.short()
    cb: sr.short()
    ig: sr.short()
    bow: sr.short()
    hbg: sr.short()
    lbg: sr.short()
    unk: sr.int()

class Lbr(sr.AnnotatedStruct):
    iceborneBytes: sr.int()
    unk: sr.ushort()
    entries: sr.DynamicList(LbrEntry)

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