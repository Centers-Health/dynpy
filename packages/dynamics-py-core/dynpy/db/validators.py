from datetime import date, datetime

from django.core.validators import MinValueValidator
from django.forms import ValidationError


class FourDigitYearValidator(MinValueValidator):
    message = "Must be a four-digit year."

    def __init__(self, *args, **kwargs):
        super().__init__(1000, *args, **kwargs)

    def __call__(self, value: date | datetime):
        year = self.clean(value)
        limit_value = self.limit_value
        message = self.message
        suggestion = self.get_suggestion(year)
        if suggestion:
            message += f" {suggestion}"

        params = {"limit_value": limit_value, "show_value": year, "value": value}
        if self.compare(year, limit_value):
            raise ValidationError(message, code=self.code, params=params)

    def clean(self, value: date | datetime):
        return value.year

    def get_suggestion(self, year: int) -> str | None:
        """
        Returns a 4 digit year suggestion if the input is a 2 digit year.
        If the the input year is less than or equal to the current 2 digit year it
        suggests the current century, otherwise it suggests the previous century.
        """
        suggestion = "Did you mean {year}?"
        if len(str(year)) == 2:
            current_year = date.today().year
            suggested_year = current_year - (current_year % 100) + year
            if suggested_year > current_year:
                suggested_year -= 100
            return suggestion.format(year=suggested_year)
