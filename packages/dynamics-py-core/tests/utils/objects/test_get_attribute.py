from dynpy.utils.objects import get_attribute


def setup():
    class object1:
        name = "John"

    class object2:
        obj1 = object1()

    class object3:
        obj2 = object2()

    return object3


def test_get_attribute_returns_attribute():
    obj3 = setup()
    name = get_attribute(obj3, "obj2", "obj1", "name")
    assert name == "John"


def test_get_attribute_returns_None_if_attribute_is_none_and_no_default():
    obj3 = setup()
    obj3.obj2 = None
    attr = get_attribute(obj3, "obj2")
    assert attr is None


def test_get_attribute_returns_default_if_attribute_is_none():
    obj3 = setup()
    obj3.obj2 = None
    attr = get_attribute(obj3, "obj2", default="default")
    assert attr == "default"


def test_attribute_errors_returns_default():
    obj3 = setup()
    attr = get_attribute(obj3, "aaa", "obj2", default="default")
    assert attr == "default"


def test_attribute_does_not_return_default_if_False():
    class obj:
        val = False

    attr = get_attribute(obj, "val")
    assert attr is False
