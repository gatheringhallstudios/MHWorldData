import unittest
import os
import shutil

from src.data import (set_languages, set_data_path, get_data_path, 
    load_base_map, load_data_map, load_split_data_map)

import json

test_base = [
    {
        'name': { 'en': 'test1', 'ja': 'test1j' }
    },
    {
        'name': { 'en': 'test2', 'ja': 'test2j' }
    },
    {
        'name': { 'en': 'test3', 'ja': 'test3j' }
    }
]

test_data = {}
for item in test_base:
    test_data[item['name']['en']] = { 'data': item['name']['en'] }

def save_json(obj, path_in_datapath):
    path = get_data_path(path_in_datapath)
    with open(path, 'w') as f:
        json.dump(obj, f)

class TestLoading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs('tmpload', exist_ok=True)
        set_languages(['en', 'ja'])
        set_data_path('tmpload')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('tmpload')
        
    def test_load_base_map(self):
        save_json(test_base, 'tbase.json')

        bmap = load_base_map('tbase.json')
        self.assertEqual(len(bmap), len(test_base), msg="Expected map and base to match")

    def test_load_base_map_has_auto_ids(self):
        save_json(test_base, 'tbaseidt.json')

        bmap = load_base_map('tbaseidt.json')

        idval = bmap.id_of('ja', 'test2j')
        self.assertEqual(idval, 2, msg="expected auto id to have value 2")

    def test_load_data_map(self):
        save_json(test_base, 'tbasedm.json')
        save_json(test_data, 'tdm.json')

        bmap = load_base_map('tbasedm.json')
        datamap = load_data_map(bmap, 'tdm.json')

        self.assertEqual(len(datamap), len(bmap), msg="expecting full join")
        for i in range(1, len(datamap) + 1):
            bmap_name = bmap[i].name('en')
            self.assertEqual(datamap[i].name('en'), bmap_name, msg=f"expecting names to match for entry {i}")
            self.assertEqual(datamap[i]['data'], bmap_name, msg="expected data to match the name")

    def test_load_data_map_skips_nonexisting_entries(self):
        save_json(test_base, 'tbasedmskip.json')
        save_json({ 'test2': test_data['test2']}, 'tdataskipped.json')

        bmap = load_base_map('tbasedmskip.json')
        datamap = load_data_map(bmap, 'tdataskipped.json')

        self.assertEqual(len(datamap), 1, "expected one entry in the data map")
        
        item = datamap.entry_of('en', 'test2')
        self.assertEqual(item['data'], 'test2', msg="expected one entry to be test2")

    def test_load_split_data_map(self):
        save_json(test_base, 'tbasedmskip.json')
        os.makedirs('tmpload/split/')
        save_json({ 'test2': test_data['test2']}, 'split/split1.json')
        save_json({ 'test1': test_data['test1']}, 'split/split2.json')

        bmap = load_base_map('tbasedmskip.json')
        datamap = load_split_data_map(bmap, 'split')

        self.assertEqual(len(datamap), 2, "expected two entries in the data map")

        names = [entry.name('en') for entry in datamap.values()]
        self.assertEqual(names, ['test1', 'test2'], msg="Expected names to match in basemap order")
