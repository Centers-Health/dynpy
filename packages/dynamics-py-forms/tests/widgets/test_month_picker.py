import pytest
from dynpy_forms.widgets import (
    MonthPicker,
    MonthPickerLastDay,
    MonthTypeableLastDayWidget,
    MonthTypeableWidget,
)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("2024-04", "2024-04-01"),
        ("", ""),
        (None, None),
    ],
)
def test_month_picker_value_from_datadict_well_formed(raw_value, expected):
    widget = MonthPicker()
    assert widget.value_from_datadict({"month": raw_value}, {}, "month") == expected


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("2024-04", "2024-04-30"),
        ("", ""),
        (None, None),
    ],
)
def test_month_picker_last_day_value_from_datadict_well_formed(raw_value, expected):
    widget = MonthPickerLastDay()
    assert widget.value_from_datadict({"month": raw_value}, {}, "month") == expected


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("04/2024", "2024-04"),
        ("12/2025", "2025-12"),
        ("2024-04", "2024-04"),
        ("", ""),
        (None, None),
        ("not-a-date", "not-a-date"),
        ("04/2024/01", "04/2024/01"),
        ("13/2024", "13/2024"),
        (123, 123),
    ],
)
def test_normalize_month_picker_value(raw_value, expected):
    assert MonthTypeableWidget._normalize_month_picker_value(raw_value) == expected


def test_month_typeable_widget_normalizes_mm_yyyy_to_first_day():
    widget = MonthTypeableWidget()
    assert widget.value_from_datadict({"month": "04/2024"}, {}, "month") == "2024-04-01"


def test_month_typeable_last_day_widget_normalizes_mm_yyyy_to_last_day():
    widget = MonthTypeableLastDayWidget()
    assert widget.value_from_datadict({"month": "04/2024"}, {}, "month") == "2024-04-30"


@pytest.mark.parametrize(
    "raw_value",
    [
        "05/2026",
        "not-a-date",
        "2024",
        "2024-04-01-02",
    ],
)
def test_month_typeable_last_day_widget_malformed_does_not_raise(raw_value):
    """
    Malformed values (e.g. mm/yyyy submitted instead of yyyy-mm, which can happen
    from stale bookmarked URLs or a desynced typeable widget) must not blow up the
    request with an unhandled ValueError. They should pass through unchanged so
    the field's own validation can report them as a normal form error.
    """
    widget = MonthTypeableLastDayWidget()
    if raw_value == "05/2026":
        assert widget.value_from_datadict({"month": raw_value}, {}, "month") == "2026-05-31"
    else:
        assert widget.value_from_datadict({"month": raw_value}, {}, "month") == raw_value
