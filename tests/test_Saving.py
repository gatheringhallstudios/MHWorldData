import pytest
import os
import shutil

from mhdata.io import DataMap, DataReaderWriter, DataStitcher

languages = ['en', 'ja']

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
    new_data = writer.load_base_json('testbase.json', languages)

    assert dict(data) == dict(new_data), "saved data didn't match"


def test_save_base_csv_symmetric(writer : DataReaderWriter):
    # Note: CSVs do not save typing info, so everything is strings
    data = DataMap()
    data.insert(create_entry_en('test1', { 'id': '1' }))
    data.insert(create_entry_en('test2', { 'id': '2' }))

    groups = ['name', 'description']
    writer.save_base_map_csv('testbase.csv', data,  groups=groups)
    new_data = writer.load_base_csv('testbase.csv', languages, groups=groups)

    assert data.to_list() == new_data.to_list(), "saved data didn't match"

def test_save_data_csv_symmetric_listmode(writer: DataReaderWriter):
    basedata = DataMap()
    basedata.add_entry(1, create_entry_en('test1'))
    basedata.add_entry(2, create_entry_en('test2'))

    extdata = DataMap()
    extdata.add_entry(1, {
        **basedata[1],
        'data': [
            {'a': 'test1'}
        ]
    })
    extdata.add_entry(2, {
        **basedata[2],
        'data': [
            {'a': 'test2'},
            {'a': 'test2ext'}
        ]
    })

    writer.save_data_csv('testdatasym.csv', extdata, key='data')
    new_data = (DataStitcher(writer)
        .use_base(basedata.copy())
        .add_csv('testdatasym.csv', key='data')
        .get())

    old_data = extdata.to_dict()
    abc = new_data.to_dict()

    assert extdata.to_dict() == new_data.to_dict(), "expected data to match"
