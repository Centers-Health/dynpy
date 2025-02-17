from django.test import TestCase
from dynpy.strawberry_django_jwt.path import PathDict, filter_strings


class FilterStringsTests(TestCase):
    def test_filter_strings(self):
        items = filter_strings(["0", "1", 0, "2"])

        assert isinstance(items, tuple)
        assert 0 not in items


class PathDictTests(TestCase):
    def setUp(self):
        self.path_dict = PathDict()

    def test_repr(self):
        path_dict_repr = f"<{self.path_dict.__class__.__name__}: {{}}>"
        assert repr(self.path_dict) == path_dict_repr

    def test_insert(self):
        self.path_dict.insert(["0", 0, "1"], True)
        assert self.path_dict["0", "1"]

    def test_parent(self):
        assert self.path_dict.parent(["0"]) is None

        parent_path = ["0", "1"]
        self.path_dict.insert(parent_path, True)

        current_path = parent_path + ["2", 0, "3"]
        value = self.path_dict.parent(current_path)

        assert value
        assert self.path_dict["0", "1", "2"]
