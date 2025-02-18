from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from dynpy_forms.fields import ValidatedDateRangeField


@pytest.mark.parametrize(
    ("dates"),
    [
        (slice(datetime(2022, 1, 1, 0, 0), datetime(2022, 7, 1, 0, 0))),
        (slice(datetime(2022, 2, 1, 0, 0), datetime(2022, 2, 1, 0, 0))),
    ],
)
def test_start_date_is_before_end_date_does_not_throw_exception(dates):
    field = ValidatedDateRangeField()

    field.validate(dates)


def test_start_date_is_after_end_date_throws_exception():
    value = slice(datetime(2022, 7, 1, 0, 0), datetime(2022, 1, 1, 0, 0))

    field = ValidatedDateRangeField()

    with pytest.raises(ValidationError) as e:
        field.validate(value)
    assert e.value.message == "Start date cannot be after end date"
