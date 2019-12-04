import pytest
import os
import shutil

import json

from mhdata.io import DataReader

languages = ['en', 'ja']

def save_json(obj, path):
    with open(path, 'w') as f:
        json.dump(obj, f)

@pytest.fixture()
def loader_mock(tmpdir):
    "Returns loader pointed to a temporary directory created for the test"
    return DataReader(
        data_path=tmpdir,
        languages=languages,
    )

def test_load_base_json(loader_mock, basedata):
    path = loader_mock.get_data_path('base.json')
    save_json(basedata, path)

    bmap = loader_mock.load_base_json('base.json', languages)
    assert len(bmap) == len(basedata), "Expected map and base to match"

def test_load_base_json_has_auto_ids(loader_mock, basedata):
    path = loader_mock.get_data_path('base.json')
    save_json(basedata, path)

    bmap = loader_mock.load_base_json('base.json', languages)

    idval = bmap.id_of('ja', 'test2j')
    assert idval == 2, "expected auto id to have value 2"

def test_load_data_json(loader_mock, basedata, subdata):
    save_json(basedata, loader_mock.get_data_path('base.json'))
    save_json(subdata, loader_mock.get_data_path('data.json'))

    bmap = loader_mock.load_base_json('base.json', languages)
    datamap = loader_mock.load_data_json(bmap.copy(), 'data.json')

    assert len(datamap) == len(bmap), "expecting full join"
    for i in range(1, len(datamap) + 1):
        bmap_name = bmap[i].name('en')
        assert datamap[i].name('en') == bmap_name, f"expecting names to match for entry {i}"
        assert datamap[i]['data'] == bmap_name, "expected data to match the name"
