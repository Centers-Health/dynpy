import pytest
from bs4 import BeautifulSoup
from dynpy_gfl.filters import TabFilter, TabFilterWithCounts
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.views import GenericFilterListView
from dynpy_gfl.widgets import TabRadioSelect

pytestmark = pytest.mark.django_db


"""
Fixtures
"""


@pytest.fixture
def status_choices():
    return [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]


@pytest.fixture
def user_filterset_with_tabs_filter_declared(status_choices, django_user_model):
    """Filterset with tabs_filter as a declared filter"""

    class UserFiltersetWithTabsFilter(GenericFilterSet):
        tabs_filter = TabFilter(choices=status_choices, method="filter_by_tab")

        class Meta:
            model = django_user_model
            fields = ["username", "first_name"]

        def filter_by_tab(self, queryset, name, value):
            # Dummy filter method for testing
            return queryset

    return UserFiltersetWithTabsFilter


@pytest.fixture
def user_filterset_without_tabs_filter(django_user_model):
    """Filterset without any tabs_filter"""

    class UserFiltersetWithoutTabsFilter(GenericFilterSet):
        class Meta:
            model = django_user_model
            fields = ["username", "first_name"]

    return UserFiltersetWithoutTabsFilter


@pytest.fixture
def user_filterset_with_tabs_filter_with_counts(status_choices, django_user_model):
    """Filterset with TabFilterWithCounts"""

    class UserFiltersetWithTabsFilterWithCounts(GenericFilterSet):
        tabs_filter = TabFilterWithCounts(choices=status_choices, method="filter_by_tab")

        class Meta:
            model = django_user_model
            fields = ["username", "first_name"]

        def filter_by_tab(self, queryset, name, value):
            # Dummy filter method for testing
            return queryset

    return UserFiltersetWithTabsFilterWithCounts


"""
TabFilter Tests
"""


def describe_tab_filter():
    def adding_empty_label(status_choices):
        tab_filter = TabFilter(choices=status_choices, empty_label="All")
        choices = list(tab_filter.field.choices)
        assert choices[0] == ("", "All")

    def it_can_set_custom_ul_class(status_choices):
        tab_filter = TabFilter(choices=status_choices, ul_class="custom-nav-class")
        assert tab_filter.field.widget.ul_class == "custom-nav-class"

    def it_uses_default_ul_class_when_not_specified(status_choices):
        tab_filter = TabFilter(choices=status_choices)
        assert tab_filter.field.widget.ul_class == "nav nav-tabs nav-justified mb-3"


"""
TabRadioSelect Widget Tests
"""


def describe_tab_radio_select_widget():
    def it_has_default_ul_class():
        widget = TabRadioSelect()
        assert widget.ul_class == "nav nav-tabs nav-justified mb-3"

    def it_can_set_custom_ul_class():
        widget = TabRadioSelect(ul_class="my-custom-class")
        assert widget.ul_class == "my-custom-class"

    def it_includes_ul_class_in_context():
        widget = TabRadioSelect(ul_class="test-class")
        context = widget.get_context("test", None, {})
        assert context["ul_class"] == "test-class"

    def it_hides_radio_inputs_with_d_none_class():
        widget = TabRadioSelect()
        assert widget.attrs.get("class") == "d-none"


"""
View tabs_filter Tests
"""


def describe_view_tabs_filter():
    def it_returns_tabs_filter_when_declared_as_filter(
        rf, django_user_model, user_filterset_with_tabs_filter_declared
    ):
        class TestView(GenericFilterListView):
            model = django_user_model
            filterset_class = user_filterset_with_tabs_filter_declared
            template_name = "dynpy_gfl/generic_filter_list_htmx.html"

        request = rf.get("/")
        view = TestView()
        view.setup(request)
        view.object_list = view.get_queryset()
        view.get(request)

        tabs_filter = view.tabs_filter
        assert tabs_filter is not None
        assert tabs_filter.name == "tabs_filter"

    def it_returns_none_when_no_tabs_filter(rf, django_user_model, user_filterset_without_tabs_filter):
        class TestView(GenericFilterListView):
            model = django_user_model
            filterset_class = user_filterset_without_tabs_filter
            template_name = "dynpy_gfl/generic_filter_list_htmx.html"

        request = rf.get("/")
        view = TestView()
        view.setup(request)
        view.object_list = view.get_queryset()
        view.get(request)

        assert view.tabs_filter is None


"""
Template Rendering Tests
"""


def describe_template_rendering():
    def it_renders_tabs_when_tabs_filter_is_defined(
        rf, django_user_model, user_filterset_with_tabs_filter_declared
    ):
        class TestView(GenericFilterListView):
            model = django_user_model
            filterset_class = user_filterset_with_tabs_filter_declared
            template_name = "dynpy_gfl/generic_filter_list_htmx.html"
            base_template = "tests/dummy_base.html"

        request = rf.get("/")
        response = TestView.as_view()(request)
        soup = BeautifulSoup(response.render().content, features="html.parser")

        tabs_container = soup.find("div", {"id": "gfl-tabs"})
        assert tabs_container is not None

    def it_does_not_render_tabs_container_when_no_tabs_filter(
        rf, django_user_model, user_filterset_without_tabs_filter
    ):
        class TestView(GenericFilterListView):
            model = django_user_model
            filterset_class = user_filterset_without_tabs_filter
            template_name = "dynpy_gfl/generic_filter_list_htmx.html"
            base_template = "tests/dummy_base.html"

        request = rf.get("/")
        response = TestView.as_view()(request)
        soup = BeautifulSoup(response.render().content, features="html.parser")

        tabs_container = soup.find("div", {"id": "gfl-tabs"})
        assert tabs_container is None

    def it_excludes_tabs_filter_from_regular_filters(
        rf, django_user_model, user_filterset_with_tabs_filter_declared
    ):
        """tabs_filter should not appear in the regular filter form"""

        class TestView(GenericFilterListView):
            model = django_user_model
            filterset_class = user_filterset_with_tabs_filter_declared
            template_name = "dynpy_gfl/generic_filter_list_htmx.html"
            base_template = "tests/dummy_base.html"

        request = rf.get("/")
        response = TestView.as_view()(request)
        soup = BeautifulSoup(response.render().content, features="html.parser")

        # tabs_filter should be in the tabs container, not in basicFilters form inputs
        basic_filters_form = soup.find("form", {"id": "basicFilters"})
        # Look for input with name "tabs_filter" directly in the form row (not in gfl-tabs)
        form_row = basic_filters_form.find("div", {"class": "form-row"})

        # The tabs_filter input should NOT be in the form-row div as a regular filter field
        # It should only appear in the gfl-tabs container
        tabs_in_form_row = form_row.find("input", {"name": "tabs_filter"}) if form_row else None
        tabs_in_tabs_container = soup.find("div", {"id": "gfl-tabs"})

        # Tabs should be in the tabs container
        assert tabs_in_tabs_container is not None
        # But the filter field wrapper should not be in the regular form area
        # (the hidden input may still be there for form submission, but not as a visible filter)
        assert tabs_in_form_row is None


def describe_ul_class_rendering():
    """Tests for ul_class customization in templates"""

    def it_renders_default_ul_class(rf, django_user_model, user_filterset_with_tabs_filter_declared):
        class TestView(GenericFilterListView):
            model = django_user_model
            filterset_class = user_filterset_with_tabs_filter_declared
            template_name = "dynpy_gfl/generic_filter_list_htmx.html"
            base_template = "tests/dummy_base.html"

        request = rf.get("/")
        response = TestView.as_view()(request)
        soup = BeautifulSoup(response.render().content, features="html.parser")

        tabs_ul = soup.find("ul", {"class": "nav nav-tabs nav-justified mb-3"})
        assert tabs_ul is not None

    def it_renders_custom_ul_class(rf, django_user_model, status_choices):
        class CustomFilterset(GenericFilterSet):
            tabs_filter = TabFilter(
                choices=status_choices, ul_class="custom-tabs-class", method="filter_by_tab"
            )

            class Meta:
                model = django_user_model
                fields = ["username"]

            def filter_by_tab(self, queryset, name, value):
                return queryset

        class TestView(GenericFilterListView):
            model = django_user_model
            filterset_class = CustomFilterset
            template_name = "dynpy_gfl/generic_filter_list_htmx.html"
            base_template = "tests/dummy_base.html"

        request = rf.get("/")
        response = TestView.as_view()(request)
        soup = BeautifulSoup(response.render().content, features="html.parser")

        tabs_ul = soup.find("ul", {"class": "custom-tabs-class"})
        assert tabs_ul is not None


"""
Default Tab Selection Tests
"""


def describe_default_tab_selection():
    def it_selects_empty_label_by_default(status_choices, django_user_model):
        """TabFilter defaults to empty_label='All', so '' should be auto-selected"""

        class FiltersetWithTabs(GenericFilterSet):
            tabs_filter = TabFilter(choices=status_choices, method="filter_by_tab")

            class Meta:
                model = django_user_model
                fields = ["username"]

            def filter_by_tab(self, queryset, name, value):
                return queryset

        filterset = FiltersetWithTabs()
        # Empty label (All) is selected by default
        assert filterset.data.get("tabs_filter") == ""

    def it_selects_first_choice_when_empty_label_disabled(status_choices, django_user_model):
        """When empty_label=None, first real choice should be selected"""

        class FiltersetWithTabs(GenericFilterSet):
            tabs_filter = TabFilter(choices=status_choices, empty_label=None, method="filter_by_tab")

            class Meta:
                model = django_user_model
                fields = ["username"]

            def filter_by_tab(self, queryset, name, value):
                return queryset

        filterset = FiltersetWithTabs()
        # First real choice is selected when no empty label
        assert filterset.data.get("tabs_filter") == "active"

    def it_allows_custom_empty_label(status_choices, django_user_model):
        """Custom empty label should work and be selected by default"""

        class FiltersetWithTabs(GenericFilterSet):
            tabs_filter = TabFilter(
                choices=status_choices, empty_label="Show All", method="filter_by_tab"
            )

            class Meta:
                model = django_user_model
                fields = ["username"]

            def filter_by_tab(self, queryset, name, value):
                return queryset

        filterset = FiltersetWithTabs()
        # Empty label is selected by default
        assert filterset.data.get("tabs_filter") == ""

    def it_does_not_set_default_when_no_tabs_filter(django_user_model):
        """No default should be set when tabs_filter is not defined"""

        class FiltersetWithoutTabs(GenericFilterSet):
            class Meta:
                model = django_user_model
                fields = ["username"]

        filterset = FiltersetWithoutTabs()
        assert filterset.data.get("tabs_filter") is None
