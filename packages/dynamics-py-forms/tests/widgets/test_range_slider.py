import pytest

from dynpy_forms.widgets import RangeSliderWidget


@pytest.mark.parametrize(
    ("value", "min", "max"),
    [
        ([None, None], 0, 100),
        ([50, None], 50, 100),
        ([None, 75], 0, 75),
        ([50, 75], 50, 75),
    ],
)
def test_value_label_shows_correct_min_and_max_for_value_given(value, min, max):
    """
    If either the min or the max is None the label should show the default min/max
    instead of showing NaN.
    """
    rsw = RangeSliderWidget()
    attrs = {"data_range_min": 0, "data_range_max": 100, "id": 1}
    context = rsw.get_context("test slider", value, attrs)

    value_label = context["widget"]["value_label"]

    assert value_label == f"{min} - {max}"
