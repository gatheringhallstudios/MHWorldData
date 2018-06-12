import pytest
import mhdata.util as util

def test_group_fields():
    item = { 'level': 2, 'description_en': 'test', 'description_ja': None }
    grouped = util.group_fields(item, groups=('description',))

    expected = { 'level': 2, 'description': { 'en': 'test', 'ja': None } }
    assert grouped == expected, "description should have been grouped"
