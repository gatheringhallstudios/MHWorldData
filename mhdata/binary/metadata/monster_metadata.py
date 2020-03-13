import json
from typing import Iterable

from os.path import dirname, abspath, join

from mhdata.io.csv import read_csv


class MonsterMetaEntry:
    def __init__(self, name, id, id_alt, key_name, key_description):
        self.name = name
        self.id = id
        self.id_alt = id_alt
        self.key_name = key_name
        self.key_description = key_description

class MonsterMetadata:
    """
        Attempt to load the various types of mappings that monsters have
    Monsters have an internal numerical id used in some schemas, and varying string ids
    used in other schemas. Note that string key sare inconsistent, so some magic is usually involved.
    Therefore we load:
    - Map keyed by name_en that gives the string keys for names and for hunter notes (can differ)
    - Map keyed by internal id that connects to name_en (used for hitzones/statuses/etc)
    """

    def __init__(self):
        id_alt_keys = ['id_alt', 'id_alt2']

        this_dir = dirname(abspath(__file__))

        # Load data from the quest data dump project
        # Note that since the key is a FILEPATH it can't be joined with the rest of the data
        self.monster_data_ext = json.load(open(this_dir + '/metadata_files/MonsterData.json'))

        monster_keys_csv = read_csv(this_dir + '/metadata_files/monster_map.csv')
        monster_entries = [MonsterMetaEntry(
            name=r['name_en'].strip(),
            id=int(r['id'], 16),
            id_alt=[int(r[key], 16) for key in id_alt_keys if r[key]],
            key_name=r['key_name'],
            key_description=r['key_description']
        ) for r in monster_keys_csv]

        self._map = dict((r.name, r) for r in monster_entries)
        self._map_by_id = dict((r.id, r) for r in monster_entries)

        # Add alt keys. Note that they only go one way and cannot be reverse associated
        for r in monster_entries:
            for alt_id in r.id_alt:
                self._map_by_id[alt_id] = r

    def has_monster(self, monster_name):
        return monster_name in self._map.keys()

    def has_monster_id(self, monster_id):
        return monster_id in self._map_by_id.keys()

    def by_id(self, id) -> MonsterMetaEntry:
        return self._map_by_id[id]

    def by_name(self, name) -> MonsterMetaEntry:
        return self._map[name]

    def entries(self) -> Iterable[MonsterMetaEntry]:
        for entry in self._map.values():
            yield entry

    def get_ext(self, path_key):
        return self.monster_data_ext['Monsters'].get(path_key)

    def get_part(self, path_key, part_id):
        data_ext = self.get_ext(path_key)
        if not data_ext:
            return None

        try:
            return data_ext['PartStringIds'][part_id]
        except IndexError:
            return 'OUT OF BOUNDS'