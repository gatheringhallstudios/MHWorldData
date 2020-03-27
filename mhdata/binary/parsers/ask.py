
from . import structreader as sr

class AskEntry(sr.AnnotatedStruct):
    icon_id: sr.int()
    color_id: sr.int()
    order: sr.int()
    item_id: sr.uint()
    entry_id: sr.int() # something to do with ASP
    item2_id: sr.uint() # unsure
    num_gem_slots: sr.ubyte()
    gem_slot1_lvl: sr.ubyte()
    gem_slot2_lvl: sr.ubyte()
    gem_slot3_lvl: sr.ubyte()

    @property
    def slots(self):
        return [getattr(self, f'gem_slot{i+1}_lvl') for i in range(self.num_gem_slots)]

class Ask(sr.AnnotatedStruct):
    iceborneBytes: sr.int()
    filetype: sr.ushort()
    entries: sr.DynamicList(AskEntry)