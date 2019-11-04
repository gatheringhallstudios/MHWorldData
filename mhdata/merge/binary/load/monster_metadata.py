from os.path import dirname, abspath, join

from mhdata.io.csv import read_csv


class MonsterMetaEntry:
    def __init__(self, name, id, key_name, key_description):
        self.name = name
        self.id = id
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
        this_dir = dirname(abspath(__file__))
        monster_keys_csv = read_csv(this_dir + '/monster_map.csv')
        monster_entries = [MonsterMetaEntry(
            name=r['name_en'],
            id=int(r['id'], 16),
            key_name=r['key_name'],
            key_description=r['key_description']
        ) for r in monster_keys_csv]

        # todo: handle alt keys
        self._map = dict((r.name, r) for r in monster_entries)
        self._map_by_id = dict((r.id, r) for r in monster_entries)

    def has_monster(self, monster_name):
        return monster_name in self._map.keys()

    def by_id(self, id) -> MonsterMetaEntry:
        return self._map_by_id[id]

    def by_name(self, name) -> MonsterMetaEntry:
        return self._map[name]