import pytest
import os
import shutil

from src.data import DataMap, DataReaderWriter

def create_entry(name_map):
    return { 'name': name_map }

def create_entry_en(name):
    return create_entry({ 'en': name })

@pytest.fixture()
def writer(tmpdir):
    "Returns a reader/writer pointed to a temporary directory created for the test"
    return DataReaderWriter(
        data_path=tmpdir,
        languages=['en']
    )

def test_save_base_symmetric(writer):
    data = DataMap()
    data.add_entry(1, create_entry_en('test1'))
    data.add_entry(2, create_entry_en('test2'))

    writer.save_base_map('testbase.json', data)
    new_data = writer.load_base_map('testbase.json')

    assert dict(data) == dict(new_data), "saved data didn't match"

def test_save_data_map_symmetric(writer):
    basedata = DataMap()
    basedata.add_entry(1, create_entry_en('test1'))
    basedata.add_entry(2, create_entry_en('test2'))

    extdata = DataMap()
    extdata.add_entry(1, { 'name': { 'en': 'test1' }, 'data': 'test1'})
    extdata.add_entry(2, { 'name': { 'en': 'test2' }, 'data': 'test2'})

    writer.save_data_map('testdatasym.json', basedata, extdata)
    new_data = writer.load_data_map(basedata, 'testdatasym.json')

    assert dict(extdata) == dict(new_data), "expected data to match"

def test_save_split_data_map_symmetric(writer):
    basedata = DataMap()
    basedata.add_entry(1, create_entry_en('test1'))
    basedata.add_entry(2, create_entry_en('test2'))

    extdata = DataMap()
    extdata.add_entry(1, { 'name': { 'en': 'test1' }, 'key': 'f1', 'data': 'test1'})
    extdata.add_entry(2, { 'name': { 'en': 'test2' }, 'key': 'f2', 'data': 'test2'})

    writer.save_split_data_map('split', basedata, extdata, 'key')
    new_data = writer.load_split_data_map(basedata, 'split')

    assert dict(extdata) == dict(new_data), "expected data to match"
