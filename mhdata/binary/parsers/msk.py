from pathlib import Path

from . import structreader as sr
from .decrypt import CapcomBlowfish

MSK_MSKE_KEY = b'qm7psvaMXQoay7kARXpNPcLNWqsbqcOyI4lqHtxFh26HSuE6RHNq7J4e'

# Note index to color mapping
note_colors = ['P', 'R', 'O', 'Y', 'G', 'B', 'C', 'W', 'E']
note_map = { -1: 'D', **{ i:n for i,n in enumerate(note_colors)} }

class MskEntry(sr.AnnotatedStruct):
    STRUCT_SIZE = 20
    id: sr.uint()
    note1: sr.MappedValue(sr.int(), note_map)
    note2: sr.MappedValue(sr.int(), note_map)
    note3: sr.MappedValue(sr.int(), note_map)
    note4: sr.MappedValue(sr.int(), note_map)

    @property
    def note_str(self):
        notes = []
        for i in range(4):
            note = getattr(self, f'note{i+1}')
            if note == 'D':
                break
            notes.append(note)
        return ''.join(notes)


class Msk(sr.AnnotatedStruct):
    "Binary type for monster hitzone data"
    iceborneBytes: sr.int()
    magic: sr.ushort()
    entries: sr.DynamicList(MskEntry)


class MskeEntry(sr.AnnotatedStruct):
    id: sr.int()
    dur0: sr.float()
    dur1: sr.float()
    dur2: sr.float()
    ext0: sr.float()
    ext1: sr.float()
    ext2: sr.float()
    effect1: sr.float()
    effect2: sr.float()
    name_gmd: sr.uint()
    effect1_gmd: sr.uint()
    effect2_gmd: sr.uint()
    unk1: sr.uint()
    unk2: sr.uint()


class Mske(sr.AnnotatedStruct):
    iceborneBytes: sr.int()
    magic: sr.short()
    entriesRaw: sr.DynamicList(MskeEntry) # note: the first is a dummy

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._entries = None

    @property
    def entries(self):
        if self._entries is None:
            self._entries = self.entriesRaw[1:]
        return self._entries


def load_msk(filepath):
    filepath = Path(filepath)
    data = CapcomBlowfish(open(filepath,'rb').read(), MSK_MSKE_KEY)
    return sr.StructReader(data).read_struct(Msk)


def load_mske(filepath):
    filepath = Path(filepath)
    data = CapcomBlowfish(open(filepath,'rb').read(), MSK_MSKE_KEY)
    return sr.StructReader(data).read_struct(Mske)