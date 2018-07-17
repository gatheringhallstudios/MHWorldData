import pytest
import os
import shutil

from mhdata.io import DataMap, DataReaderWriter

def create_entry(name_map, extra={}):
    return { 'name': name_map, 'description': name_map, **extra }

def create_entry_en(name, extra={}):
    return create_entry({ 'en': name, 'ja': name+'ja' }, extra)

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
    new_data = writer.load_base_json('testbase.json')

    assert dict(data) == dict(new_data), "saved data didn't match"


def test_save_base_csv_symmetric(writer : DataReaderWriter):
    # Note: CSVs do not save typing info, so everything is strings
    data = DataMap()
    data.insert(create_entry_en('test1', { 'id': '1' }))
    data.insert(create_entry_en('test2', { 'id': '2' }))

    groups = ['name', 'description']
    writer.save_base_map_csv('testbase.csv', data,  groups=groups)
    new_data = writer.load_base_csv('testbase.csv', groups=groups)

    assert data.to_list() == new_data.to_list(), "saved data didn't match"


def test_save_data_json_symmetric(writer):
    basedata = DataMap()
    basedata.add_entry(1, create_entry_en('test1'))
    basedata.add_entry(2, create_entry_en('test2'))

    extdata = DataMap()
    extdata.add_entry(1, { **basedata[1], 'data': 'test1'})
    extdata.add_entry(2, { **basedata[2], 'data': 'test2'})

    writer.save_data_json('testdatasym.json', extdata, fields=['data'])

    testdata = writer.load_data_json(basedata.copy(), 'testdatasym.json')

    assert extdata.to_dict() == testdata.to_dict(), "expected data to match"


def test_save_data_csv_symmetric_listmode(writer: DataReaderWriter):
    basedata = DataMap()
    basedata.add_entry(1, create_entry_en('test1'))
    basedata.add_entry(2, create_entry_en('test2'))

    extdata = DataMap()
    extdata.add_entry(1, {
        **basedata[1],
        'data': [
            {'data': 'test1'}
        ]
    })
    extdata.add_entry(2, {
        **basedata[2],
        'data': [
            {'data': 'test2'},
            {'data': 'test2ext'}
        ]
    })

    writer.save_data_csv('testdatasym.csv', extdata, key='data')
    new_data = writer.load_data_csv(basedata.copy(), 'testdatasym.csv', key='data', leaftype="list")

    assert extdata.to_dict() == new_data.to_dict(), "expected data to match"


def test_save_split_data_map_symmetric(writer):
    basedata = DataMap()
    basedata.add_entry(1, create_entry_en('test1'))
    basedata.add_entry(2, create_entry_en('test2'))

    extdata = DataMap()
    extdata.add_entry(1, { **basedata[1], 'key': 'f1', 'data': 'test1'})
    extdata.add_entry(2, { **basedata[2], 'key': 'f2', 'data': 'test2'})

    writer.save_split_data_map('split', basedata, extdata, 'key')
    new_data = writer.load_split_data_map(basedata, 'split')

    assert extdata.to_dict() == new_data.to_dict(), "expected data to match"
