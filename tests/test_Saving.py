import pytest
import os
import shutil

from src.data import DataMap

from src.data import (set_languages, set_data_path, get_data_path, 
    load_base_map, load_data_map, load_split_data_map, 
    save_base_map, save_data_map, save_split_data_map)

def create_test_entry(name_map):
    return { 'name': name_map }

def create_test_entry_en(name):
    return create_test_entry({ 'en': name })

class TestSaving():
    "Tests the save methods. It assumes that the load functions work"
    # Note: This is a very basic test, especially since the save methods are not part of the build process
    # The save methods are for personal use whenever I am pulling new data from other sources.

    @pytest.fixture(autouse=True, scope='session')
    def setUpClass(self):
        try:
            os.makedirs('tmpsave', exist_ok=True)
            set_languages(['en'])
            set_data_path('tmpsave')

            # Runs the actual tests
            yield

        finally:
            shutil.rmtree('tmpsave')

    def test_save_base_symmetric(self):
        data = DataMap()
        data.add_entry(1, create_test_entry_en('test1'))
        data.add_entry(2, create_test_entry_en('test2'))

        save_base_map('testbase.json', data)
        new_data = load_base_map('testbase.json')

        assert dict(data) == dict(new_data), "saved data didn't match"

    def test_save_data_map_symmetric(self):
        basedata = DataMap()
        basedata.add_entry(1, create_test_entry_en('test1'))
        basedata.add_entry(2, create_test_entry_en('test2'))

        extdata = DataMap()
        extdata.add_entry(1, { 'name': { 'en': 'test1' }, 'data': 'test1'})
        extdata.add_entry(2, { 'name': { 'en': 'test2' }, 'data': 'test2'})

        save_data_map('testdatasym.json', basedata, extdata)
        new_data = load_data_map(basedata, 'testdatasym.json')

        assert dict(extdata) == dict(new_data), "expected data to match"

    def test_save_split_data_map_symmetric(self):
        basedata = DataMap()
        basedata.add_entry(1, create_test_entry_en('test1'))
        basedata.add_entry(2, create_test_entry_en('test2'))

        extdata = DataMap()
        extdata.add_entry(1, { 'name': { 'en': 'test1' }, 'key': 'f1', 'data': 'test1'})
        extdata.add_entry(2, { 'name': { 'en': 'test2' }, 'key': 'f2', 'data': 'test2'})

        save_split_data_map('split', basedata, extdata, 'key')
        new_data = load_split_data_map(basedata, 'split')

        assert dict(extdata) == dict(new_data), "expected data to match"