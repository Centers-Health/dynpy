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
from dynpy_forms.widgets import BootstrapSelectOrAddNew, MultipleFileInput, SwitchWidget, TypeAheadSelect


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
