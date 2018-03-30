import unittest

from src.data import DataMap

def test_entry(name_map):
    return { 'name': name_map }

def test_entry_en(name):
    return test_entry({ 'en': name })

class TestDataMap(unittest.TestCase):
    def test_starts_with_zero_length(self):
        map = DataMap()
        self.assertEqual(len(map), 0, msg="Expected empty map")

    def test_add_entries_adds_length(self):
        map = DataMap()
        map.add_entry(0, test_entry_en("test1"))
        map.add_entry(1, test_entry_en("test2"))
        self.assertEqual(len(map), 2, msg="expected 2 entries to exist")

    def test_can_lookup_by_id(self):
        map = DataMap()
        map.add_entry(0, test_entry_en("test1"))
        map.add_entry(1, test_entry_en("test2"))
        map.add_entry(2, test_entry_en("test3"))

        found = map[1]
        self.assertEqual(found.name('en'), "test2", msg="found name should match")

    def test_can_lookup_id_by_name(self):
        map = DataMap()
        map.add_entry(0, test_entry_en("test1"))
        map.add_entry(1, test_entry_en("test2"))
        map.add_entry(2, test_entry_en("test3"))

        idval = map.id_of("en", "test2")
        self.assertEqual(idval, 1, msg="expected test 2 to have id 1")

    def test_can_lookup_entry_by_name(self):
        map = DataMap()
        map.add_entry(0, test_entry_en("test1"))
        map.add_entry(1, test_entry_en("test2"))
        map.add_entry(2, test_entry_en("test3"))

        entry = map.entry_of("en", "test2")
        self.assertEqual(entry.name('en'), 'test2', msg="expected entry name to match")
        self.assertEqual(entry.id, 1, msg="expected entry to have id 1")

    def test_can_iterate_values_in_order(self):
        expected_entries = [
            (1, test_entry_en('test1')),
            (2, test_entry_en("test2")),
            (3, test_entry_en("test3"))]
        
        map = DataMap()
        for (id, entry) in expected_entries:
            map.add_entry(id, entry)
        
        found = [(id, entry) for (id, entry) in map.items()]
        self.assertEqual(found, expected_entries, msg="Expected map entries to match")