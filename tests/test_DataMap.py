import pytest

from mhdata.io import DataMap

def create_test_entry(name_map, extradata={}):
    return { 'name': name_map, **extradata }

def create_test_entry_en(name, extradata={}):
    return create_test_entry({ 'en': name }, extradata)


def test_starts_with_zero_length():
    map = DataMap()
    assert not len(map), "Expected empty map"

def test_add_entries_adds_length():
    map = DataMap()
    map.insert(create_test_entry_en("test1"))
    map.insert(create_test_entry_en("test2"))
    assert len(map) == 2, "expected 2 entries to exist"

def test_nonmatching_id_throws():
    map = DataMap()
    with pytest.raises(ValueError):
        test_entry = create_test_entry_en("test1")
        map.add_entry(1, { **test_entry, 'id': 25})

def test_uses_provided_id():
    map = DataMap()
    map.insert({ 'id': 3, **create_test_entry_en("test1") })

    assert 3 in map.keys(), "entry should have used id 3"

def test_can_lookup_by_id():
    map = DataMap()
    map.add_entry(55, create_test_entry_en("test1"))
    map.add_entry(1, create_test_entry_en("test2"))
    map.add_entry(8, create_test_entry_en("test3"))

    found = map[1] # note: id order is not sequential
    assert found.name('en') == "test2", "found name should match"

def test_can_lookup_id_by_name():
    map = DataMap()
    map.add_entry(1, create_test_entry_en("test1"))
    map.add_entry(2, create_test_entry_en("test2"))
    map.add_entry(3, create_test_entry_en("test3"))

    idval = map.id_of("en", "test2")
    assert idval == 2, "expected test 2 to have id 1"

def test_can_lookup_entry_by_name():
    map = DataMap()
    map.insert(create_test_entry_en("test1"))
    map.insert(create_test_entry_en("test2"))
    map.insert(create_test_entry_en("test3"))

    entry = map.entry_of("en", "test2")
    assert entry.name('en') == 'test2', "expected entry name to match"

def test_can_iterate_values_in_order():
    expected_entries = [
        (1, create_test_entry_en('test1')),
        (2, create_test_entry_en("test2")),
        (3, create_test_entry_en("test3"))]
    
    map = DataMap()
    for (id, entry) in expected_entries:
        map.add_entry(id, entry)
    
    found = [(id, entry) for (id, entry) in map.items()]
    assert found == expected_entries, "Expected map entries to match"

def test_set_value_after_item():
    test_keys = [ 'test1', 'test2', 'test3', 'test4']
    test_dict = { k:1 for k in test_keys }
    test_dict['name'] = { 'en': 'a test' } # required field

    datamap = DataMap()
    entry = datamap.add_entry(1, test_dict)

    entry.set_value('NEW', 1, after='test2')

    # note: name exists because it was manually added to test_dict
    expected_keys = ['test1', 'test2', 'NEW', 'test3', 'test4', 'name']
    entry_keys = list(entry.keys())
    assert entry_keys == expected_keys, "Expected new to be after test2"

def test_manual_id_resets_sequence():
    datamap = DataMap()

    datamap.add_entry(25, create_test_entry_en('test1'))
    new_entry = datamap.insert(create_test_entry_en('test2'))

    assert new_entry.id > 25, "new id should have been higher"

def test_to_dict_correct_data():
    data = {
        25: create_test_entry_en('test1', { 'somedata': {'nested': 5}}),
        28: create_test_entry_en('test2', { 'somedata': {'alsonested': 'hey'}})
    }

    datamap = DataMap()
    datamap.add_entry(25, data[25])
    datamap.add_entry(28, data[28])

    serialized = datamap.to_dict()
    assert serialized == data, "expected serialized data to match original data"

def test_clone_returns_equal_map():
    data = {
        25: create_test_entry_en('test1', { 'somedata': {'nested': 5}}),
        28: create_test_entry_en('test2', { 'somedata': {'alsonested': 'hey'}})
    }

    datamap = DataMap(data)
    cloned_datamap = datamap.copy()

    assert datamap.to_dict() == cloned_datamap.to_dict(), "expected clone to match"
    assert id(datamap) != id(cloned_datamap), "expecting clone to be a different object"

def test_merge_adds_data():
    baseData = {
        1: create_test_entry_en('test1'),
        2: create_test_entry_en('test2'),
        3: create_test_entry_en('test3')
    }
    datamap = DataMap(baseData.copy())

    extendedData = {
        'test1': { 'extended': 2 },
        'test3': { 'extended': 3 }
    }

    datamap.merge(extendedData)

    assert datamap[1]['extended'] == 2, 'expected data 1 to get extended'
    assert datamap[3]['extended'] == 3, 'expected data 3 to get extended'
    assert datamap[2] == baseData[2], 'expected data 2 to not update'
    

def test_merge_adds_data_key():
    # same as the non-key test, but tests that it occured under the key
    baseData = {
        1: create_test_entry_en('test1'),
        2: create_test_entry_en('test2'),
        3: create_test_entry_en('test3')
    }
    datamap = DataMap(baseData.copy())

    extendedData = {
        'test1': { 'extended': 2 },
        'test3': { 'extended': 3 }
    }

    datamap.merge(extendedData, key="test")

    assert datamap[1]['test']['extended'] == 2, 'expected data 1 to get extended'
    assert datamap[3]['test']['extended'] == 3, 'expected data 3 to get extended'
    assert datamap[2] == baseData[2], 'expected data 2 to not update'
