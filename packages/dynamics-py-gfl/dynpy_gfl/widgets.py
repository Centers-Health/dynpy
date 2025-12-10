from django.forms import RadioSelect

from dynpy_gfl.hx_requests import QuerySetCountHx


class InlineButtonRadioSelect(RadioSelect):
    """A radio select that looks like bootstrap buttons"""

    template_name = "dynpy_gfl/widgets/button_radio_select.html"
    option_template_name = "dynpy_gfl/widgets/button_radio_option.html"

    def __init__(self, attrs=None, choices=()):
        base_attrs = {"class": "btn-check"}
        if attrs:
            base_attrs.update(attrs)
        super().__init__(attrs=base_attrs, choices=choices)

    def use_required_attribute(self, initial):
        return False  # Bootstrap buttons shouldn't use require


class InlineButtonRadioSelectWithCounts(InlineButtonRadioSelect):
    """
    An button radio select that includes counts for each option.
    This intended to be used in a generic filter list view.

    NOTE: This widget expects `request` to be passed in the context when rendering.
    The `render_with_context` template tag from dynpy_forms can be used to do this.
    """

    template_name = "dynpy_gfl/widgets/button_radio_select_with_counts.html"
    option_template_name = "dynpy_gfl/widgets/button_radio_option_with_count.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["count_hx_name"] = QuerySetCountHx.name
        context["hx_include"] = "#basicFilters"
        return context


class TabRadioSelect(RadioSelect):
    """A radio select that renders as Bootstrap nav-tabs"""

    template_name = "dynpy_gfl/widgets/tab_radio_select.html"
    option_template_name = "dynpy_gfl/widgets/tab_radio_option.html"
    default_ul_class = "nav nav-tabs nav-justified mb-3"

    def __init__(self, attrs=None, choices=(), ul_class=None):
        self.ul_class = ul_class or self.default_ul_class
        base_attrs = {"class": "d-none"}  # Hide actual radio inputs
        if attrs:
            base_attrs.update(attrs)
        super().__init__(attrs=base_attrs, choices=choices)

    def use_required_attribute(self, initial):
        return False

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["ul_class"] = self.ul_class
        return context


class TabRadioSelectWithCounts(TabRadioSelect):
    """
    A tab radio select that includes counts for each option.
    This is intended to be used in a generic filter list view.

    NOTE: This widget expects `request` to be passed in the context when rendering.
    The `render_with_context` template tag from dynpy_forms can be used to do this.
    """

    template_name = "dynpy_gfl/widgets/tab_radio_select_with_counts.html"
    option_template_name = "dynpy_gfl/widgets/tab_radio_option_with_count.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["count_hx_name"] = QuerySetCountHx.name
        context["hx_include"] = "#basicFilters"
        return context
