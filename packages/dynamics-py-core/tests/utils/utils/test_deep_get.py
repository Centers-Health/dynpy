import pytest
from dynpy.utils.itertools import deep_get


@pytest.mark.parametrize(
    ("data", "path", "expected", "default_value"),
    [
        # Basic dictionary and path tests
        ({"a": {"b": {"c": 1}}}, "a.b.c", 1, None),
        ({"a": {"b": {"c": 1}}}, ["a", "b", "c"], 1, None),
        # Missing keys, should return None
        ({"a": {"b": {"c": 1}}}, "a.x.y", None, None),
        ({"a": {"b": {"c": 1}}}, ["a", "x", "y"], None, None),
        # None values
        ({"a": {"b": None}}, "a.b.y", None, None),
        ({"a": {"b": None}}, ["a", "b", "y"], None, None),
        # List index tests
        ({"a": [{"b": 2}]}, "a.0.b", 2, None),
        ({"a": [{"b": 2}]}, ["a", 0, "b"], 2, None),
        ({"a": [{"b": 2}]}, "a.1.b", None, None),  # Out-of-bound list index
        ({"a": [{"b": 2}]}, ["a", 1, "b"], None, None),
        # Default value tests
        ({"a": {"b": {"c": 1}}}, "a.x.y", "not_found", "not_found"),
        ({"a": [{"b": 2}]}, "a.1.b", "default", "default"),
        # Type handling: invalid list index
        ({"a": [{"b": 2}]}, ["a", "x", "b"], None, None),  # Invalid index for list
        ({"a": [{"b": 2}]}, "a.x.b", None, None),  # Invalid index string instead of int
        # Complex nested structures
        ({"a": {"b": [{"c": 1}]}}, "a.b.0.c", 1, None),
        ({"a": {"b": [{"c": 1}]}}, ["a", "b", 0, "c"], 1, None),
        # Edge cases: empty dictionaries and lists
        ({}, "a.b.c", None, None),  # Empty dictionary
        ({}, ["a", "b", "c"], None, None),
        ({"a": []}, "a.0", None, None),  # Empty list inside dictionary
    ],
)
def test_deep_get(data, path, expected, default_value):
    assert deep_get(data, path, default=default_value) == expected
