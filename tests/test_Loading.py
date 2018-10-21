import pytest
import os
import shutil

import json

from mhdata.io import DataReader

def save_json(obj, path):
    with open(path, 'w') as f:
        json.dump(obj, f)

@pytest.fixture()
def loader_mock(tmpdir):
    "Returns loader pointed to a temporary directory created for the test"
    return DataReader(
        data_path=tmpdir,
        languages=['en', 'ja'],
        required_languages=['en', 'ja']
    )

def test_load_base_json(loader_mock, basedata):
    path = loader_mock.get_data_path('base.json')
    save_json(basedata, path)

    bmap = loader_mock.load_base_json('base.json')
    assert len(bmap) == len(basedata), "Expected map and base to match"

def test_load_base_json_has_auto_ids(loader_mock, basedata):
    path = loader_mock.get_data_path('base.json')
    save_json(basedata, path)

    bmap = loader_mock.load_base_json('base.json')

    idval = bmap.id_of('ja', 'test2j')
    assert idval == 2, "expected auto id to have value 2"

def test_load_data_json(loader_mock, basedata, subdata):
    save_json(basedata, loader_mock.get_data_path('base.json'))
    save_json(subdata, loader_mock.get_data_path('data.json'))

    bmap = loader_mock.load_base_json('base.json')
    datamap = loader_mock.load_data_json(bmap.copy(), 'data.json')

    assert len(datamap) == len(bmap), "expecting full join"
    for i in range(1, len(datamap) + 1):
        bmap_name = bmap[i].name('en')
        assert datamap[i].name('en') == bmap_name, f"expecting names to match for entry {i}"
        assert datamap[i]['data'] == bmap_name, "expected data to match the name"

def test_load_split_data_map(loader_mock, basedata, subdata):
    save_json(basedata, loader_mock.get_data_path('base.json'))

    split_path = loader_mock.get_data_path('split/')

    os.makedirs(split_path)
    save_json({ 'test2': subdata['test2']}, os.path.join(split_path, 'split1.json'))
    save_json({ 'test1': subdata['test1']}, os.path.join(split_path, 'split2.json'))

    bmap = loader_mock.load_base_json('base.json')
    datamap = loader_mock.load_split_data_map(bmap, 'split')

    assert len(datamap) == 2, "expected two entries in the data map"

    names = [entry.name('en') for entry in datamap.values()]
    assert names == ['test1', 'test2'], "Expected names to match in basemap order"
