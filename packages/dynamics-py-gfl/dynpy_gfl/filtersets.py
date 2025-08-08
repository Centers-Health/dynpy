import re

import django_filters
from django.utils.datastructures import MultiValueDict
from django.utils.functional import cached_property
from dynpy.templatetags.dynpy_tags import field_name_to_label

from dynpy_gfl.ordering import FieldOrderByClause

from .enums import FilterListOrder


class GenericFilterSet(django_filters.FilterSet):
    """
    A filterset class that handles column ordering
    """

    columns = None
    extra_filters = None
    quick_filters = None
    default_order_fields = None
    default_order = FilterListOrder.ASC

    def get_default_filters(self, request) -> MultiValueDict:
        return MultiValueDict()

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if not self.is_filtered(data):
            data = self.get_default_filters(request)
        if self.default_order_fields:
            self._validate_default_order_fields()
        super().__init__(data, queryset, request=request, prefix=prefix)

    def _validate_default_order_fields(self):
        # Default order fields can be str or list. Ensure always a list
        defaults = (
            self.default_order_fields
            if isinstance(self.default_order_fields, list)
            else [self.default_order_fields]
        )
        for field in defaults:
            if not self._field_is_a_column(field):
                raise ValueError(
                    f"Field '{field}' in default_order_fields is not a column on the page. "
                )

    def is_filtered(self, data=None) -> bool:
        """
        Returns True if any GET params (data) overlap with any filters.
        For range filters regex is needed because the inputs have min|max|after|before
        appended to them, and therefore they do not match the name of the filter.
        """
        if not data:
            return False
        filters = self.base_filters.keys()
        params_str = " ".join(dict(data).keys())

        return any(
            re.search(rf"\b({filter})_?(min|max|after|before)?\b", params_str) for filter in filters
        )

    @cached_property
    def column_definitions(self):
        default_fields = self.Meta.fields
        if isinstance(default_fields, dict):
            default_fields = list(default_fields.keys())
        fields = self.columns or default_fields
        return [self.field_to_column_definition(field) for field in fields]

    def field_to_column_definition(self, field):
        """
        Helper method to convert the different column definitions to standard types for use in the template.
        """
        if type(field) not in [str, tuple]:
            raise TypeError(
                f"Field definition must be either a string or a tuple. It is of type {type(field).__name__}."
            )

        field_name, label, allow_ordering = None, None, True

        if isinstance(field, tuple):
            for i, val in enumerate(field):
                if i < 2:
                    if not isinstance(val, str):
                        raise ValueError(
                            f"Field definition of type tuple must have a string at index {i}. It has a {type(val).__name__}."
                        )
                else:
                    if not isinstance(val, bool):
                        raise ValueError(
                            f"Field definition of type tuple with 3 values must have a bool at index 2. It has a {type(val).__name__}."
                        )
            if len(field) > 2:
                field_name, label, allow_ordering = field
            else:
                field_name, label = field
        else:
            field_name = field
            label = field_name_to_label(field)

        return {"field_name": field_name, "label": label, "allow_ordering": allow_ordering}

    @property
    def order_by_overrides(self) -> dict:
        """
        The key should be the name of the column (not the label).
        The value should be a list of order_by fields.
        """
        return {}

    @property
    def qs(self):
        # The check here is for caching the qs and it mimics the way djanog_filters does it.
        if not hasattr(self, "_qs"):
            qs = super().qs
            if self.Meta:
                order_fields = self.get_order_fields()
                order_by = self.get_order_by(order_fields, self.request_order)

                qs = qs.order_by(*order_by)
            self._qs = qs
        return self._qs

    @property
    def request_order(self):
        if self.request and self.request.GET.get("order", None) in FilterListOrder.__members__:
            return FilterListOrder[self.request.GET.get("order")]
        return None

    def get_order_by(self, order_fields, request_order):
        order = request_order or self.default_order
        has_reverse_order_fields = any(isinstance(field, str) and "-" in field for field in order_fields)

        order_by_params = []
        # Remove fields that are not columns
        order_fields = [field for field in order_fields if self._field_is_a_column(field)]
        for field in order_fields:
            field_order = order
            # Need to process '-' on page load
            if isinstance(field, str):
                if not request_order and has_reverse_order_fields:
                    field_order = FilterListOrder.DESC if "-" in field else FilterListOrder.ASC
                field = field.replace("-", "")

            field_override = self.order_by_overrides.get(field, field)
            field_order_by_params = []

            if isinstance(field_override, list):
                for field in field_override:
                    field_order_by_params.append(FieldOrderByClause(field, field_order).process_field())
            else:
                field_order_by_params.append(
                    FieldOrderByClause(field_override, field_order).process_field()
                )

            order_by_params.extend(field_order_by_params)
        return order_by_params

    def _field_is_a_column(self, field):
        # Checks if the given field is one of the columns on the page.
        column_names = [column.get("field_name") for column in self.column_definitions]
        # Strip the leading "-" from the name if it has one.
        field_without_direction = field[1:] if field.startswith("-") else field
        return field_without_direction in column_names

    def get_order_fields(self):
        order_fields = self.default_order_fields

        # If no defaults use first column that is not an empty string
        if order_fields is None and len(self.column_definitions) > 0:
            order_fields = [
                next(
                    (col.get("field_name") for col in self.column_definitions if col.get("field_name")),
                    None,
                )
            ]

        if self.request:
            request_order_by = self.request.GET.get("order_by", None)
            if request_order_by:
                order_fields = [request_order_by]
        return order_fields
