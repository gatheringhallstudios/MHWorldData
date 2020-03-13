from typing import Iterable, Tuple, Iterator
from pathlib import Path

from .bcore import load_schema, load_text, get_chunk_root
from ..metadata import MonsterMetadata, MonsterMetaEntry
from ..parsers import load_epg, DttEpg

class MonsterData:
    epg: DttEpg
    parts: Iterable['MonsterPart']
    unlinked_hitzones: Iterable[int]
    def __init__(self, id, name, description, meta: MonsterMetaEntry):
        self.id = id
        
        self.name = name
        self.description = description
        self.meta = meta

        self.epg = None
        self.hitzones = []
        self.parts = []
        self.unlinked_hitzones = []

    def __repr__(self):
        return f"MonsterData <{self.name.get('en')}>"

class MonsterPart:
    def __init__(
            self, id: int, name: str, flinch: int, extract: str,
            cleaves: Iterable[Tuple[str, int]],
            subparts: Iterable['MonsterSubPart']
        ):
        self.id = id
        self.name = name
        self.flinch = flinch
        self.extract = extract
        self.cleaves = cleaves
        self.subparts = subparts

class MonsterSubPart:
    def __init__(self, hzv_base: dict, hzv_broken: dict, hzv_special: Iterable[dict]):
        self.hzv_base = hzv_base
        self.hzv_broken = hzv_broken
        self.hzv_special = hzv_special

class MonsterCollection(Iterable[MonsterData]):
    monsters: Iterable[MonsterData]

    def __init__(self):
        self._metadata = MonsterMetadata()
        monster_name_text = load_text('common/text/em_names')
        monster_info_text = load_text('common/text/em_info')
        self.epg_loaded = False

        self.monsters = []
        for meta_entry in self._metadata.entries():
            key_name = meta_entry.key_name
            key_description = meta_entry.key_description
            if not key_name:
                print(f"Warning: Monster {meta_entry.name} does not have a key")
                continue

            name = monster_name_text[key_name]
            description = None

            if key_description:
                key1 = f'NOTE_{key_description}_DESC'
                key2 = f'NOTE_{key_description}DESC'
                if key1 in monster_info_text:
                    description = monster_info_text[key1]
                elif key2 in monster_info_text:
                    description = monster_info_text[key2]
                else:
                    raise KeyError(f"Could not find key for either {key1} or {key2} in monster info")
            
            monster = MonsterData(meta_entry.id, name, description, meta_entry)

            self.monsters.append(monster)

        self._monsters_by_id = { m.id:m for m in self.monsters }
        self._monsters_by_name = { m.name['en']:m for m in self.monsters }

    def load_epg_eda(self) -> bool:
        if self.epg_loaded:
            return False

        root = Path(get_chunk_root())
        for filename in root.joinpath('em/').rglob('*.dtt_epg'):
            epg_binary = load_epg(filename)

            try:
                monster = self.by_id(epg_binary.monster_id)
            except KeyError:
                continue # warn?

            monster.epg = epg_binary
            path_key = filename.stem + "_" + str(filename.parents[1].stem)

            for hitzone_id, hitzone in enumerate(epg_binary.hitzones):
                monster.hitzones.append({
                    'hitzone_id': hitzone_id,
                    'cut': hitzone.sever,
                    'impact': hitzone.blunt,
                    'shot': hitzone.shot,
                    'fire': hitzone.fire,
                    'water': hitzone.water,
                    'thunder': hitzone.thunder,
                    'ice': hitzone.ice,
                    'dragon': hitzone.dragon,
                    'ko': hitzone.stun
                })

            unlinked = set(range(len(monster.hitzones)))
            def get_hitzone(idx):
                if idx == -1:
                    return None
                hitzone = monster.hitzones[idx]
                if idx in unlinked:
                    unlinked.remove(idx)
                return hitzone

            for part_id, part in enumerate(epg_binary.parts):
                part_name = self._metadata.get_part(path_key, part_id) or f"UNK_PART_{part_id}"

                cleaves = []
                for cleave_idx in part.iter_cleaves():
                    if cleave_idx == -1: continue
                    cleave = epg_binary.cleaves[cleave_idx]
                    if cleave.damage_type == 'any': continue
                    cleaves.append((cleave.damage_type, cleave.special_hp))

                subparts = []
                for s in part.subparts:
                    for subpart in [s.sub_base, s.sub_unknown]:
                        special_hzvs = []
                        if monster.name['en'] not in ['Behemoth']:
                            for special_idx in range(3):
                                value = getattr(subpart, 'hzv_special' + str(special_idx+1))
                                hzv_spec = get_hitzone(value)
                                if hzv_spec: special_hzvs.append(hzv_spec)
                        
                        subparts.append(MonsterSubPart(
                            hzv_base=get_hitzone(subpart.hzv_base),
                            hzv_broken=get_hitzone(subpart.hzv_broken),
                            hzv_special=special_hzvs
                        ))
                
                new_part = MonsterPart(
                    part_id, part_name, part.flinchValue, part.extract, cleaves, subparts)
                monster.parts.append(new_part)

            monster.unlinked_hitzones = list(unlinked)

        return True

    def by_id(self, binary_id) -> MonsterData:
        return self._monsters_by_id[binary_id]

    def by_name(self, name_en) -> MonsterData:
        return self._monsters_by_name[name_en]

    def __len__(self):
        return len(self.monsters)

    def __iter__(self) -> Iterator[MonsterData]:
        yield from self.monsters