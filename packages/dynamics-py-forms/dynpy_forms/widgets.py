import uuid
from calendar import monthrange
from datetime import date
from typing import Any

from django.forms import ClearableFileInput, Select, Widget, widgets
from django.forms.models import ModelChoiceIterator
from django.forms.widgets import HiddenInput
from django.http import QueryDict
from django.template import loader
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django_filters.widgets import DateRangeWidget, RangeWidget, SuffixedMultiWidget


class MonthPicker(Widget):
    template_name = "dynpy_forms/widgets/month_picker.html"

    def __init__(self, attrs=None):
        attrs = attrs or {}
        if attrs.get("show_clear_button"):
            attrs.update({"style": "padding-right:1.1rem;"})
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        if isinstance(value, date) or not value:
            context["widget"]["month_value"] = value.strftime("%Y-%m") if value else ""
        else:
            context["widget"]["month_value"] = value[:-3]

        return context

    def value_from_datadict(self, data, files, name):
        """Actual value is the first day of the month"""
        monthyear = super().value_from_datadict(data, files, name)
        return f"{monthyear}-01" if monthyear else monthyear


class MonthPickerLastDay(MonthPicker):
    def value_from_datadict(self, data, files, name):
        """Actual value is the last day of the month"""
        monthyear = data.get(name)
        if not monthyear:
            return monthyear
        year, month = map(int, monthyear.split("-"))
        last_day = monthrange(year, month)[1]
        return f"{monthyear}-{last_day}"


class BootstrapSelect(widgets.Select):
    template_name = "dynpy_forms/widgets/multiselect.html"

    def __init__(
        self,
        option_template=None,
        item_name_plural=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.item_name_plural = item_name_plural
        # set default attributes
        self.attrs.setdefault("class", "selectpicker form-control")
        self.attrs.setdefault("data-style", "custom-select")
        self.attrs.setdefault("data-live-search", "true")
        self.attrs.setdefault("data-live-search-placeholder", "Search...")
        self.attrs.setdefault("data-actions-box", "true")
        self.attrs.setdefault("data-deselect-all-text", "None")
        self.attrs.setdefault("data-select-all-text", "All")
        self.attrs.setdefault("data-none-selected-text", "All")
        self.attrs.setdefault("data-dropup-auto", "false")
        self.attrs.setdefault("data-selected-text-format", "count")

        # Template path or raw HTML to be used for displaying options in
        # the select list (optional). Renders as a data attribute wrapped
        # in single quotes, so **single quotes in the template must be escaped**
        # To have the full object in the html/template use the
        # FullObjectSelectField with the widget.
        self.option_template = option_template

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

    def get_context(self, name, value, attrs):
        attrs = attrs or {}
        if not self.item_name_plural and isinstance(self.choices, ModelChoiceIterator):
            self.item_name_plural = self.choices.queryset.model._meta.verbose_name_plural
        self.item_name_plural = self.item_name_plural or "items"
        attrs["data-count-selected-text"] = f"{{0}} {self.item_name_plural.title()} selected"
        context = super().get_context(name, value, attrs)
        context["option_template"] = self.option_template
        context["widget"]["choices"] = self.choices
        context["random_id"] = f"bootstrapselect-{uuid.uuid4()}"
        return context


class BootstrapMultiSelect(BootstrapSelect):
    allow_multiple_selected = True


class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


class TypeAheadSelect(BootstrapSelect):
    """
    Select widget that fetches results as text is typed into the search input.
    Requires a GraphQL query name for fetching options.
    The query schema must take a SearchInput and return a SearchResultSet.

    Example query schema:
    ```
    @gql.type
    class Query:
        @gql.django.field(permission_classes=[HasAPIKey])
        def facilities(self, search_input: SearchInput) -> SearchResultSet:
            facilities = Facility.objects.filter(name__istartswith=search_input.search_term)[
                : search_input.limit
            ]
            result_list = [SearchResult(key=f.pk, value=f.name) for f in facilities]
            return SearchResultSet(count=search_input.count, results=result_list)
    ```
    """

    template_name = "dynpy_forms/widgets/typeahead_select.html"

    def __init__(self, query_name=None, *args, **kwargs):
        kwargs["attrs"] = kwargs.get("attrs") or {}
        kwargs["attrs"].setdefault("data-none-selected-text", "None selected")
        kwargs["attrs"].setdefault("data-live-search-placeholder", "Type to search...")

        super().__init__(*args, **kwargs)
        self.query_name = query_name

    def get_context(self, name, value, attrs):
        if value:
            # if used by ModelChoiceField
            if hasattr(self.choices, "queryset"):
                model = self.choices.queryset.model
                self.choices.queryset = model.objects.filter(pk=value)
            else:
                self.choices = [(value, value)]
                self.choices = [("", "---------"), (value, value)]

        context = super().get_context(name, value, attrs)
        context["query"] = self.query_name
        return context


class BootstrapSelectOrAddNew(BootstrapSelect):
    def __init__(self, *args, name="option", **kwargs):
        super().__init__(*args, **kwargs)
        link_style = "color: var(--primary); text-decoration: underline;"
        self.attrs["data-none-results-text"] = (
            f'<a style="{link_style}" onclick="bootstrapSelectAddNew(this)">'
            f"Add <b>{{0}}</b> as new {name}"
            "</a>"
        )

    class Media:
        js = ("dynpy_forms/js/select_add_new.js",)


class SubmitButtonSelect(widgets.ChoiceWidget):
    """
    Select that renders out the options as submit buttons.

    Need to pass label into widget and not the field that is
    using the widget.
    Pass 'name' into the attrs of the widget to change the 'name' of
    all the buttons.
    Pass 'drop_right' into the attrs to render the dropdown on the right.

    Special choices:
        '------' (6 dashes) will render a dropdown divider
        '#' will render a dropdown header
        'custom{}'(has to start with word custom) will render
            whatever is put into the choice as plain html (will
            not wrap it in a submit button)
    """

    template_name = "dynpy_forms/widgets/submit_button_select.html"

    def __init__(self, label="Select", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label

        self.attrs.setdefault("class", "btn btn-secondary btn-sm dropdown-toggle")
        self.attrs.setdefault("type", "button")
        self.attrs.setdefault("data-toggle", "dropdown")

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["choices"] = self.choices
        context["widget"]["label"] = self.label
        context["widget"]["name"] = self.attrs.get("name") or context["widget"]["name"]
        context["drop_right"] = self.attrs.get("drop_right")
        return context


class NullableSelect(Select):
    """
    Select widget that adds an empty option labeled "---------"
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = (("", ("---------")), *kwargs["choices"])


class RangeSliderWidget(RangeWidget):
    template_name = "dynpy_forms/widgets/range_slider.html"

    def __init__(self, attrs=None):
        widgets = (HiddenInput(), HiddenInput())
        super(RangeWidget, self).__init__(widgets, attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Set current min/max values
        data_range_min = context["widget"]["attrs"]["data_range_min"]
        data_range_max = context["widget"]["attrs"]["data_range_max"]

        # value is None on initial page load
        if value is None:
            cur_min, cur_max = data_range_min, data_range_max
        else:
            cur_min = value[0] if value[0] is not None else data_range_min
            cur_max = value[1] if value[1] is not None else data_range_max

        context["widget"]["attrs"].update(
            {
                "data_cur_min": cur_min,
                "data_cur_max": cur_max,
            }
        )

        # Set ids of min/max subwidgets
        widget_id = context["widget"]["attrs"]["id"]
        for i, subwidget in enumerate(context["widget"]["subwidgets"]):
            subwidget["attrs"]["id"] = f"{widget_id}_{self.suffixes[i]}"

        # Set value label
        context["widget"]["value_label"] = f"{cur_min} - {cur_max}"
        return context

    class Media:
        css = {
            "all": (
                "dynpy_forms/vendor/jquery_ui_range_slider.min.css",
                "dynpy_forms/css/range_slider.css",
            )
        }
        js = (
            "dynpy_forms/vendor/jquery_ui_range_slider.min.js",
            "dynpy_forms/js/range_slider.js",
        )


class InlineRangeWidget(RangeWidget):
    """An inline version of the RangeWidget that renders both fields on the same line"""

    template_name = "dynpy_forms/widgets/inline_range_widget.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets[0].attrs.update({"placeholder": "min", "class": "multiwidget"})
        self.widgets[1].attrs.update({"placeholder": "max", "class": "multiwidget"})


class SwitchWidget(widgets.CheckboxInput):
    """
    Widget used in SwitchField.
    """

    template_name = "dynpy_forms/widgets/switch.html"

    def __init__(self, attrs=None, check_test=None, **kwargs) -> None:
        super().__init__(attrs=attrs, check_test=check_test)
        self.css_classes = kwargs.pop("css_classes", None)
        self.css_styles = kwargs.pop("css_styles", None)

    def get_context(self, name: str, value: Any, attrs) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        context["css_classes"] = self.css_classes
        context["css_styles"] = self.css_styles
        return context

    def value_from_datadict(self, data: dict[str, Any], files, name: str) -> Any:
        datadict_value = data.get(name)
        if datadict_value in ["on", True]:
            return True
        elif datadict_value in ["off", False]:
            return False
        else:
            # Handles None case
            return super().value_from_datadict(data, files, name)


class DateRangePicker(DateRangeWidget):
    template_name = "dynpy_forms/widgets/date_range_picker.html"

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Value must be a list of values corresponding to
        # start and end date, both of which can be None.
        if not isinstance(value, list):
            value = self.decompress(value)

        context["widget"]["start_date"] = value[0] if value[0] else ""
        context["widget"]["end_date"] = value[1] if value[1] else ""

        return context


class InlineMonthRangeWidget(SuffixedMultiWidget):
    suffixes = ["after", "before"]
    template_name = "dynpy_forms/widgets/inline_range_widget.html"

    def get_widgets(self):
        """Return the widgets to be used for the range."""
        return (MonthPicker, MonthPicker)

    def __init__(self, attrs=None):
        attrs = attrs or {}
        widgets = self.get_widgets()
        super().__init__(widgets, attrs)
        self.widgets[0].attrs.update({"class": "multiwidget"})
        self.widgets[1].attrs.update({"class": "multiwidget"})

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]


class InlineMonthRangeLastDayWidget(InlineMonthRangeWidget):
    def get_widgets(self):
        return (MonthPicker, MonthPickerLastDay)


class DashedBooleanWidget(widgets.NullBooleanSelect):
    """
    BooleanWidget that uses the label "---------" instead of "Unknown" when nothing is selected to
    match django_filters.ChoiceFilter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = (("____", ("---------")), ("true", ("Yes")), ("false", ("No")))


class GroupAwareBootstrapMultiSelect(BootstrapMultiSelect):
    """
    Group-aware bootstrap-select widget.

    - Shows all options in a group as selected when the group is active
    - Injects hidden <input> fields for group_* values so only they get submitted
      (the JS hook clears option selections before submit)
    """

    @property
    def group_key(self):
        return self.attrs["data-group-key"]

    @property
    def group_prefix(self):
        return self.attrs["data-group-prefix"]

    def __init__(self, attrs=None, **kwargs):
        super().__init__(attrs=attrs, **kwargs)

        existing_classes = self.attrs.get("class", "")
        self.attrs["class"] = f"{existing_classes} selectpicker-group-aware"

    def value_from_datadict(self, data, files, name):
        if not data:
            return []

        values = super().value_from_datadict(data, files, name) or []

        if isinstance(data, QueryDict):
            group_values = data.getlist(self.group_key, [])
        else:
            group_values = val.split(",") if (val := data.get(self.group_key)) else []

        # Encode group tokens distinctly
        return values + [f"{self.group_key}:{v}" for v in group_values]

    def render(self, name, value, attrs=None, renderer=None):
        value = value or []
        group_tokens, normal_values = [], []

        for v in value:
            (group_tokens if v.startswith(self.group_prefix) else normal_values).append(v)

        # Base rendering
        html = super().render(name, normal_values, attrs, renderer)

        if group_tokens:
            group_values = sorted({token.split(":", 1)[1] for token in group_tokens})
            hidden_html = "".join(
                f'<input type="hidden" class="group-injected" name="{escape(self.group_key)}" value="{escape(v)}">'
                for v in group_values
            )
            html += hidden_html

        return html
