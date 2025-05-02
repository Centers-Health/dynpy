from typing import Dict, List

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.aggregates import Count
from django.utils.datastructures import MultiValueDict

from dynpy_gfl.dataclasses import FilterByField


class TotalsFilterMixin:
    use_filtered_qs_in_field = True

    @property
    def field(self):
        self.add_totals_to_choices()
        return super().field

    def add_totals_to_choices(self):
        # To prevent extra db querying, only add totals once the qs has been filtered & cached
        if hasattr(self.parent, "_qs"):
            totals = self.get_totals_by_choice()
            self.extra["choices"] = [
                (choice, f"{label} ({totals[str(choice)]})")
                for choice, label in self.extra.get("choices")
            ]

    def get_totals_by_choice(self) -> Dict[str, int]:
        pk_field = self.model._meta.pk.name
        aggregate_params = {
            str(choice): Count(pk_field, filter=Q(**{f"{self.field_name}__{self.lookup_expr}": choice}))
            for choice, _ in self.extra.get("choices")
        }
        return self.parent._qs.aggregate(**aggregate_params)


class FilteredChoicesMixin:
    """
    Mixin to be used with a ModelChoiceFilter that filters the choices by other filters
    in the filterset.

    filter_by_fields: Fields to filter the choices by.

    See dynpy_gfl.filters.FilteredModelChoiceFilter for a usage example.
    """

    def __init__(
        self,
        filter_by_fields: List[FilterByField],
        *args,
        default_empty=False,
        **kwargs,
    ):
        self.filter_by_fields = filter_by_fields
        self.default_empty = default_empty
        super().__init__(*args, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        data = self.parent.data or MultiValueDict()
        filter_clause = {}
        is_default = True
        for filter_field in self.filter_by_fields:
            filter_name = filter_field.filter_name
            field_name = filter_field.field_name
            lookup_expr = f"__{filter_field.lookup_expr}" if filter_field.lookup_expr else ""
            filter_method = filter_field.filter_method

            if self.parent.filters.get(filter_field.filter_name):
                value = self.get_filter_value(data, filter_name)
                if not self.is_empty(value):
                    is_default = False
                if filter_method:
                    queryset = filter_method(queryset, filter_name, value)
                else:
                    filter_clause[field_name + lookup_expr] = value

        if is_default and self.default_empty:
            return queryset.none()

        return queryset.filter(**filter_clause).distinct()

    def is_empty(self, value):
        if isinstance(value, (list, tuple)):
            return not any(value)
        return not value

    def get_filter_value(self, data, filter_name):
        filter_field = self.parent.filters[filter_name].field
        filter_widget = filter_field.widget
        value = filter_widget.value_from_datadict(data, None, filter_name)
        try:
            return filter_field.to_python(value)
        except ValidationError:
            return []
