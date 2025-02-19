from decimal import Decimal

import pytest
from dynpy_gfl.enums import NumberFormat
from dynpy_gfl.filters import AllValuesRangeFilter
from tests.models import DecimalValueModel
from tests.testing_utils.range_filter_value import RangeFilterValue

pytestmark = pytest.mark.django_db

"""
Helpers
"""


def get_decimal_value_filter(
    step=100,
    field_name="value",
    label="value",
    number_format=NumberFormat.INT,
):
    return AllValuesRangeFilter(
        model=DecimalValueModel,
        step=step,
        field_name=field_name,
        label=label,
        number_format=number_format,
    )


"""
Tests
"""


def test_sets_default_min_and_max_if_no_model_instances_exist():
    f = get_decimal_value_filter(step=100)
    assert f.field.widget.attrs["data_range_min"] == 0
    assert f.field.widget.attrs["data_range_max"] == 100


def test_rounds_min_down_to_nearest_step():
    DecimalValueModel.objects.create(value=Decimal("1050.00"))
    f = get_decimal_value_filter(step=100)
    assert f.field.widget.attrs["data_range_min"] == 1000


def test_rounds_max_up_to_nearest_step():
    DecimalValueModel.objects.create(value=Decimal("1050.00"))
    f = get_decimal_value_filter(step=100)
    assert f.field.widget.attrs["data_range_max"] == 1100


def test_passes_attributes_to_widget():
    f = get_decimal_value_filter(
        step=100, label="Aging Balance", number_format=NumberFormat.DOLLARS_ONLY
    )
    widget_attrs = f.field.widget.attrs
    assert widget_attrs["step"] == 100
    assert widget_attrs["label"] == "Aging Balance"
    assert widget_attrs["number_format"] == NumberFormat.DOLLARS_ONLY


@pytest.mark.parametrize(
    ("min_value", "max_value", "expected_count"),
    # Skipping the case where man and min are both None.
    # The filter is not used in that case and it causes an error here
    [
        (500, None, 2),
        (None, 700, 2),
        (250, 700, 1),
        (0, 2000, 3),
    ],
)
def test_filters_model_instances_by_field_value(min_value, max_value, expected_count):
    # db setup
    for value in [Decimal("100.00"), Decimal("500.00"), Decimal("1000.00")]:
        DecimalValueModel.objects.create(value=value)

    # filter setup
    f = get_decimal_value_filter(field_name="value")
    qs = DecimalValueModel.objects.all()
    results = f.filter(qs, RangeFilterValue(start=min_value, stop=max_value))

    # assert
    assert results.count() == expected_count
