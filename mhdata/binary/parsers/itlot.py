from pathlib import Path
from . import structreader as sr
from .decrypt import CapcomBlowfish

ITLOT_KEY = b"D7N88VEGEnRl0HEHTO0xMQkbeMb37arJF488lREp90WYojAONkLoxfMt"

class ItlotEntry(sr.AnnotatedStruct):
    item_ids: sr.blist(sr.ushort(), 10)
    item_quantities: sr.blist(sr.ubyte(), 10)
    item_rarities: sr.blist(sr.ubyte(), 10)
    item_animations: sr.blist(sr.ubyte(), 10)

    def iter_items(self):
        for i in range(10):
            yield (
                self.item_ids[i], 
                self.item_quantities[i],
                self.item_rarities[i],
                self.item_animations[i]
            )


class Itlot(sr.AnnotatedStruct):
    iceborneBytes: sr.int()
    magic: sr.short()
    entries: sr.DynamicList(ItlotEntry)

def load_itlot(filepath) -> Itlot:
    filepath = Path(filepath)
    data = CapcomBlowfish(open(filepath, 'rb').read(), ITLOT_KEY)
    return sr.read_struct(data, Itlot)