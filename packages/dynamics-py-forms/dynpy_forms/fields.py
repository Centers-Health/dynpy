import re
from typing import Any

from django.core.validators import RegexValidator
from django.db.models.base import Model
from django.forms import ChoiceField, FileField, ValidationError
from django.forms.fields import BooleanField, CharField
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import Widget
from django_filters.fields import DateRangeField

from dynpy_forms.field_mixins import GroupedChoicesMixin
from dynpy_forms.widgets import (
    BootstrapSelectOrAddNew,
    GroupAwareBootstrapMultiSelect,
    MultipleFileInput,
    SwitchWidget,
    TypeAheadSelect,
)


class SwitchField(BooleanField):
    """
    Boolean field that is represented by switch
    instead of checkbox.

    Can pass css_styles or css_classes when initializing
    a SwitchField. The css is rendered on the div
    wrapper around the input.
    """

    widget = SwitchWidget

    def __init__(self, *args, **kwargs):
        css_classes = kwargs.pop("css_classes", None)
        css_styles = kwargs.pop("css_styles", None)
        super().__init__(*args, **kwargs)
        self.widget = SwitchWidget(
            attrs={"label": self.label if self.label else ""},
            css_classes=css_classes,
            css_styles=css_styles,
        )
        self.label = ""
        self.required = False


class PhoneNumberField(CharField):
    def __init__(self, *args, **kwargs):
        max_length = 12
        min_length = 10
        validators = [
            RegexValidator(
                regex=r"^\d{3}(-*|\s*)\d{3}(-*|\s*)\d{4}$",
                message="Not a valid number. Correct format is ###-###-####",
            ),
        ]
        kwargs.update(
            {
                "max_length": max_length,
                "min_length": min_length,
                "validators": validators,
            }
        )
        super().__init__(*args, **kwargs)

    def clean(self, value: Any) -> Any:
        """
        Format to ###-###-####
        """
        value = super().clean(value)
        phone = re.sub(r"^(\d{3})(\d{3})(\d{4})", r"\1-\2-\3", value.replace(" ", ""))
        return phone

    def widget_attrs(self, widget: Widget) -> Any:
        attrs = super().widget_attrs(widget)
        attrs["placeholder"] = "###-###-####"
        return attrs


class FullObjectSelectField(ModelChoiceField):
    """
    Passes the full object to the widget, instead of
    just a string representation, to be used for custom
    rendering of the options in the select.
    """

    def label_from_instance(self, obj: Model) -> str:
        return obj


class OptionalChoiceField(ChoiceField):
    widget = BootstrapSelectOrAddNew

    def __init__(self, *args, name="option", **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = BootstrapSelectOrAddNew(name=name)

    def valid_value(self, value):
        return True


class TypeAheadChoiceField(ChoiceField):
    def __init__(self, query_name=None, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get("widget"):
            self.widget = TypeAheadSelect(query_name)

    def valid_value(self, value):
        if self.choices:
            return super().valid_value(value)
        return True


class TypeAheadModelChoiceField(ModelChoiceField):
    """
    ModelChoiceField that uses TypeAheadSelect widget.

    Overrides default to_python to validate
    against all objects instead of the queryset
    because the queryset should always be empty.

    Arguments:
        queryset: expected to be empty (i.e. Model.objects.none())
        (passing a queryset with all the objects would defeat the
        purpose of the TypeAheadSelect because all the choices will
        be queried initially anyway)

        query_name: for the GraphQL query to be used in the widget

        field_for_label: field name for text to display for initial value
        (should be the value of the SearchResult type returned from
        the GraphQL query)
    """

    field_for_label: str = ""

    def __init__(self, *args, query_name=None, empty_label=None, field_for_label="", **kwargs):
        super().__init__(*args, empty_label=empty_label, **kwargs)
        self.field_for_label = field_for_label
        if not kwargs.get("widget"):
            self.widget = TypeAheadSelect(query_name)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or "pk"
            if isinstance(value, self.queryset.model):
                value = getattr(value, key)
            # Should validate value against all objects instead of queryset
            # because queryset should always be empty so it doesn't preload
            # all the choices.
            value = self.queryset.model.objects.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages["invalid_choice"], code="invalid_choice") from None
        return value

    def label_from_instance(self, obj):
        return getattr(obj, self.field_for_label, str(obj))


class ValidatedDateRangeField(DateRangeField):
    def validate(self, value: Any) -> None:
        if value.start and value.stop and value.start > value.stop:
            raise ValidationError("Start date cannot be after end date")


class GroupedModelChoiceField(GroupedChoicesMixin, ModelChoiceField):
    choices = property(GroupedChoicesMixin._get_choices, ModelChoiceField._set_choices)


class GroupedModelMultiChoiceField(GroupedChoicesMixin, ModelMultipleChoiceField):
    choices = property(GroupedChoicesMixin._get_choices, ModelMultipleChoiceField._set_choices)


class FullObjectGroupedModelChoiceField(GroupedModelChoiceField, FullObjectSelectField):
    pass


class MultipleFileField(FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        self.help_text = "Browse and select one or more files."
        super().__init__(*args, **kwargs, help_text=self.help_text)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class GroupAwareModelMultipleChoiceField(GroupedModelMultiChoiceField):
    """
    A ModelMultipleChoiceField that expands "_group_*" tokens into queryset matches.
    Example:
        - value = ["3", "_group_payor:Medicaid"]
        - returns [<Payor: pk=3>, <Payor: pk=10>, <Payor: pk=11>]
        where pk 10 and 11 are Payors with hmo_type "Medicaid"
    """

    widget = GroupAwareBootstrapMultiSelect

    def __init__(
        self,
        *args,
        request=None,
        group_prefix="_group_",
        group_by_field=None,
        filter_name=None,
        **kwargs,
    ):
        self.group_prefix = group_prefix
        self.group_by_field = group_by_field
        self.request = request
        self.filter_name = filter_name

        for attr in ("group_by_field", "request", "filter_name"):
            if getattr(self, attr) is None:
                raise ValueError(f"`{attr}` is required for {self.__class__.__name__}")

        self.group_key = self.group_prefix + self.filter_name

        super().__init__(*args, group_by_field=group_by_field, **kwargs)

    def widget_attrs(self, widget):
        return {"data-group-key": self.group_key, "data-group-prefix": self.group_prefix}

    def clean(self, value):
        group_values = self._get_group_values_from_request()

        if not group_values:
            return super().clean(value)

        # Separate non-group values
        value = value or []
        normal_values = [v for v in value if not str(v).startswith(self.group_prefix)]
        cleaned_values = list(super().clean(normal_values)) if normal_values else []

        # Expand group tokens
        matches = self.queryset.filter(**{f"{self.group_by_field}__in": group_values})
        cleaned_values.extend(matches)

        return cleaned_values

    def _get_group_values_from_request(self):
        """
        Extract group tokens from the request GET or POST data.
        e.g. "group_payor" where payor is the filter_name.
        """
        data = self.request.POST if self.request.method == "POST" else self.request.GET
        return data.getlist(self.group_key, [])
