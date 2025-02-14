from datetime import date, datetime

import pytest
from django.forms import ValidationError
from dynpy.db.validators import FourDigitYearValidator
from freezegun import freeze_time


@pytest.mark.parametrize(
    "value",
    [
        date(1, 1, 1),
        date(22, 1, 1),
        date(333, 1, 1),
        datetime(444, 1, 1, 1, 1),
    ],
)
def test_raises_validation_error_for_years_with_less_than_4_digits(value):
    validator = FourDigitYearValidator()
    with pytest.raises(ValidationError):
        validator(value)


@freeze_time(date(2024, 1, 1))
@pytest.mark.parametrize(
    ("value", "suggestion"),
    [(date(20, 1, 1), "2020"), (date(99, 1, 1), "1999"), (datetime(88, 1, 1, 1, 1), "1988")],
)
def test_suggests_4_digit_year_for_2_digit_year(value, suggestion):
    validator = FourDigitYearValidator()
    with pytest.raises(ValidationError, match=f"Did you mean {suggestion}?"):
        validator(value)
