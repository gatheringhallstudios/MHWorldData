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
