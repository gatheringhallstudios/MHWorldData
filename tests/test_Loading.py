import pytest
import os
import shutil

from src.data import (set_languages, set_data_path, get_data_path, 
    load_base_map, load_data_map, load_split_data_map)

import json

def save_json(obj, path_in_datapath):
    path = get_data_path(path_in_datapath)
    with open(path, 'w') as f:
        json.dump(obj, f)

class TestLoading():
    @pytest.fixture(autouse=True, scope='session')
    def setUpClass(self):
        try:
            os.makedirs('tmpload', exist_ok=True)
            set_languages(['en', 'ja'])
            set_data_path('tmpload')
            
            # Runs the actual test
            yield

        finally:
            shutil.rmtree('tmpload')
        
    def test_load_base_map(self, basedata):
        save_json(basedata, 'tbase.json')

        bmap = load_base_map('tbase.json')
        assert len(bmap) == len(basedata), "Expected map and base to match"

    def test_load_base_map_has_auto_ids(self, basedata):
        save_json(basedata, 'tbaseidt.json')

        bmap = load_base_map('tbaseidt.json')

        idval = bmap.id_of('ja', 'test2j')
        assert idval == 2, "expected auto id to have value 2"

    def test_load_data_map(self, basedata, subdata):
        save_json(basedata, 'tbasedm.json')
        save_json(subdata, 'tdm.json')

        bmap = load_base_map('tbasedm.json')
        datamap = load_data_map(bmap, 'tdm.json')

        assert len(datamap) == len(bmap), "expecting full join"
        for i in range(1, len(datamap) + 1):
            bmap_name = bmap[i].name('en')
            assert datamap[i].name('en') == bmap_name, f"expecting names to match for entry {i}"
            assert datamap[i]['data'] == bmap_name, "expected data to match the name"

    def test_load_data_map_skips_nonexisting_entries(self, basedata, subdata):
        save_json(basedata, 'tbasedmskip.json')
        save_json({ 'test2': subdata['test2']}, 'tdataskipped.json')

        bmap = load_base_map('tbasedmskip.json')
        datamap = load_data_map(bmap, 'tdataskipped.json')

        assert len(datamap) == 1, "expected one entry in the data map"
        
        item = datamap.entry_of('en', 'test2')
        assert item['data'] == 'test2', "expected one entry to be test2"

    def test_load_split_data_map(self, basedata, subdata):
        save_json(basedata, 'tbasedmskip.json')
        os.makedirs('tmpload/split/')
        save_json({ 'test2': subdata['test2']}, 'split/split1.json')
        save_json({ 'test1': subdata['test1']}, 'split/split2.json')

        bmap = load_base_map('tbasedmskip.json')
        datamap = load_split_data_map(bmap, 'split')

        assert len(datamap) == 2, "expected two entries in the data map"

        names = [entry.name('en') for entry in datamap.values()]
        assert names == ['test1', 'test2'], "Expected names to match in basemap order"
