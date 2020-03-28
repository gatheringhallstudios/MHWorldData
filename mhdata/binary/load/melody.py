from typing import Iterable, NamedTuple

from .bcore import get_chunk_root, load_text
from ..parsers import msk


class MelodyLength(NamedTuple):
    duration: int
    extension: int


class WeaponMelody:
    def __init__(
        self, id, name, effect1, effect2, 
        base: MelodyLength,
        maestro1: MelodyLength,
        maestro2: MelodyLength,
        notes: Iterable[str]
    ):
        self.id = id
        self.name = name
        self.effect1 = effect1
        self.effect2 = effect2 if effect1 != effect2 else None
        self.base = base
        self.maestro1 = maestro1
        self.maestro2 = maestro2
        self.notes = notes


class WeaponMelodyCollection:
    melodies: Iterable[WeaponMelody]

    def __init__(self):
        song_data = msk.load_mske(get_chunk_root() + '/common/pl/music_skill_efc.mske')
        note_data = msk.load_msk(get_chunk_root() + '/hm/wp/wp05/music_skill.msk')
        song_text = load_text("common/text/vfont/music_skill")

        notes_by_id = {}
        for notes in note_data.entries:
            notes_by_id.setdefault(notes.id, [])
            notes_by_id[notes.id].append(notes.note_str)

        self.melodies = []
        for id, song in enumerate(song_data.entries):
            notes = notes_by_id.get(id, [])
            if notes:
                self.melodies.append(WeaponMelody(
                    id=id,
                    name=song_text[song.name_gmd],
                    effect1=song_text[song.effect1_gmd],
                    effect2=song_text[song.effect2_gmd],
                    base=MelodyLength(int(song.dur0), int(song.ext0)),
                    maestro1=MelodyLength(int(song.dur1), int(song.ext1)),
                    maestro2=MelodyLength(int(song.dur2), int(song.ext2)),
                    notes=notes
                ))

        # create name map, prioritize existing entries
        self._name_map = {}
        for s in self.melodies:
            if s.name['en'] not in self._name_map:
                self._name_map[s.name['en']] = s

    def __iter__(self):
        yield from self.melodies

    def by_name(self, name):
        return self._name_map[name]