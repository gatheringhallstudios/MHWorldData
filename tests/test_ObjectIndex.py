import pytest

from build.objectindex import ObjectIndex

def test_generates_ids_for_new_objects():
    reg = ObjectIndex()
    id1 = reg.id("hello")
    id2 = reg.id('hello2')

    assert id1 != id2, "ids should be unique"

def test_generates_same_id_for_equal_objects():
    reg = ObjectIndex()
    id1 = reg.id("hello")
    id2 = reg.id('hello')

    assert id1 == id2, "ids should be the same"

def test_can_use_dictionaries():
    reg = ObjectIndex()
    id1 = reg.id({'a': 25})
    id2 = reg.id({'a': 26})
    assert id1, "should have generated an id"
    assert id1 != id2, "should have generated different ids"

def test_dictionaries_are_order_insensitive():
    reg = ObjectIndex()
    id1 = reg.id({'a': 25, 'b': 26})
    id2 = reg.id({'b': 26, 'a': 25})
    assert id1 == id2, "should have generated the same id"

def test_on_new_called_if_new():
    reg = ObjectIndex()
    
    called_obj = None

    @reg.on_new()
    def flag(itemid, obj):
        nonlocal called_obj
        called_obj = obj

    reg.id('a')

    assert called_obj == 'a', "should have called on_new with object a"

def test_on_new_not_called_if_not_new():
    reg = ObjectIndex()

    reg.id('a')

    # attach event AFTER the first item is added
    called_obj = None
    @reg.on_new()
    def flag(itemid, obj):
        nonlocal called_obj
        called_obj = obj

    reg.id('a') # call again

    assert not called_obj, "should not have called on_new"
