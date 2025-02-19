from django.db.models.aggregates import Max, Min
from django_filters.filters import (
    BooleanFilter,
    ChoiceFilter,
    DateFromToRangeFilter,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
    RangeFilter,
)
from dynpy.enums import RoundingDirection
from dynpy.math import round_to_int
from dynpy_forms.fields import SwitchField, ValidatedDateRangeField
from dynpy_forms.widgets import RangeSliderWidget

from dynpy_gfl.enums import NumberFormat
from dynpy_gfl.filter_mixins import FilteredChoicesMixin, TotalsFilterMixin


class MultipleChoiceFilterWithTotals(TotalsFilterMixin, MultipleChoiceFilter):
    pass


class ChoiceFilterWithTotals(TotalsFilterMixin, ChoiceFilter):
    pass


class FilteredModelChoiceFilter(FilteredChoicesMixin, ModelChoiceFilter):
    """
    A ModelChoiceFilter that has the ability to filter the options by other filters
    in the filterset.

    Example Usage:
    Filtering the choices of a users dropdown by permissions.

    users = FilteredModelChoiceFilter(queryset = User.objects.all().order_by('email').distinct(),
            filter_by_fields = [ FilterByField('permissions', 'user_permissions', 'in') ])

    """


class FilteredModelMultipleChoiceFilter(FilteredChoicesMixin, ModelMultipleChoiceFilter):
    """
    See FilteredModelChoiceFilter above.
    """


class ValidatedDateFromToRangeFilter(DateFromToRangeFilter):
    field_class = ValidatedDateRangeField


class SwitchFilter(BooleanFilter):
    """
    Boolean Filter that uses a switch as a widget.

    Can pass css_styles or css_classes when initializing
    the a SwitchFilter. The css is rendered on the div
    wrapper around the input.
    """

    field_class = SwitchField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = self.label if self.label is not None else ""


class AllValuesRangeFilter(RangeFilter):
    widget = RangeSliderWidget

    def __init__(
        self, model, field_name, label, step=1, number_format=NumberFormat.INT, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.model = model
        self.field_name = field_name
        self.label = label
        self.step = step
        self.number_format = number_format

    @property
    def field(self):
        min_value = self.model.objects.aggregate(Min(self.field_name))[f"{self.field_name}__min"] or 0

        real_max = self.model.objects.aggregate(Max(self.field_name))[f"{self.field_name}__max"]
        default_max = min_value + self.step
        max_value = real_max or default_max

        # Round min down and max up to the nearest step so actual min and max stay within the filter
        rounded_min = round_to_int(min_value, self.step, RoundingDirection.DOWN)
        rounded_max = round_to_int(max_value, self.step, RoundingDirection.UP)

        self.extra["widget"] = RangeSliderWidget(
            attrs={
                "step": self.step,
                "label": self.label,
                "number_format": self.number_format,
                "data_range_min": rounded_min,
                "data_range_max": rounded_max,
            }
        )

        return super().field
