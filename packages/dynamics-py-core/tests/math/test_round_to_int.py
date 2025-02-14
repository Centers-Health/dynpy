import pytest
from dynpy.enums import RoundingDirection
from dynpy.math import round_to_int


@pytest.mark.parametrize(
    ("number", "nearest", "expected"),
    [
        (7, 10, 10),
        (11, 10, 20),
    ],
)
def test_rounds_up(number, nearest, expected):
    assert round_to_int(number, nearest, RoundingDirection.UP) == expected


@pytest.mark.parametrize(
    ("number", "nearest", "expected"),
    [
        (7, 10, 0),
        (11, 10, 10),
    ],
)
def test_rounds_down(number, nearest, expected):
    assert round_to_int(number, nearest, RoundingDirection.DOWN) == expected


@pytest.mark.parametrize(
    ("number", "nearest", "expected"),
    [
        (7, 10, 10),
        (11, 10, 10),
    ],
)
def test_rounds_in_default_direction(number, nearest, expected):
    assert round_to_int(number, nearest) == expected
