from dataclasses import dataclass
from typing import Optional


@dataclass
class FilterByField:
    """
    Used with FilteredChoicesMixin.

    filter_name: The name of the filter that should be used.
    field_name: The name of the field as it relates to the model of the FilteredModelChoiceFilter.
    lookup_expr: The filtering method (i.e. 'in', 'gt', 'lt' etc.)
    filter_method: A callable that takes the name of the filter, the cleaned value of the filter,
        and the queryset and returns a filtered queryset.
        `(queryset, name, value) -> queryset`

    See dynpy_gfl.filters.FilteredModelChoiceFilter for a usage example.
    """

    filter_name: str
    field_name: Optional[str] = None
    lookup_expr: Optional[str] = None
    filter_method: Optional[callable] = None
