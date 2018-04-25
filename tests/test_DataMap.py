import pytest

from mhwdata.io import DataMap

def create_test_entry(name_map):
    return { 'name': name_map }

def create_test_entry_en(name):
    return create_test_entry({ 'en': name })


def test_starts_with_zero_length():
    map = DataMap()
    assert not len(map), "Expected empty map"

def test_add_entries_adds_length():
    map = DataMap()
    map.insert(create_test_entry_en("test1"))
    map.insert(create_test_entry_en("test2"))
    assert len(map) == 2, "expected 2 entries to exist"

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