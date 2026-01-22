from typing import Any

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from dynpy_gfl.filters import TabFilter
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.views import GenericFilterListViewHX

pytestmark = pytest.mark.django_db


class TestFilterset(GenericFilterSet):
    columns = ["username", "pk"]
    default_order_fields = "pk"

    class Meta:
        fields = ["username"]
        model = get_user_model()


class TestHxView(GenericFilterListViewHX):
    template_name = "tests/dummy_gfl.html"
    filterset_class = TestFilterset
    base_template = "tests/dummy_base.html"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().order_by("pk")


@pytest.fixture(autouse=True)
def _100_users(django_user_model):
    for i in range(100):
        django_user_model.objects.create(username=f"test_user{i}")


def describe_pagination():
    def returns_first_page_when_no_position(django_user_model, rf):
        request = rf.get("/")
        response = TestHxView.as_view()(request)
        object_list = response.context_data["object_list"]
        assert len(object_list) == TestHxView.paginate_by
        assert object_list[0].username == "test_user0"
        assert object_list[9].username == "test_user9"

    def returns_second_page_when_position_is_10(django_user_model, rf):
        request = rf.get("/", {"position": 10})
        response = TestHxView.as_view()(request)
        object_list = response.context_data["object_list"]
        assert len(object_list) == 10
        assert object_list[0].username == "test_user10"
        assert object_list[9].username == "test_user19"

    def works_with_filtered_qs(django_user_model, rf):
        request = rf.get("/", {"username": "test_user1"})
        response = TestHxView.as_view()(request)
        object_list = response.context_data["object_list"]
        assert len(object_list) == 1
        assert object_list[0].username == "test_user1"

    def changes_has_next_to_false_when_no_more_pages(django_user_model, rf):
        request = rf.get("/", {"position": 100})
        response = TestHxView.as_view()(request)
        assert response.context_data["paginator"].has_next is False


def describe_index_column():
    @pytest.mark.parametrize(("include_index_column", "expected"), [(True, True), (False, False)])
    def its_displays_th_for_index_column_when_include_index_column_is_true(
        rf, include_index_column, expected
    ):
        request = rf.get("/")
        view = TestHxView
        view.include_index_column = include_index_column
        response = view.as_view()(request)
        soup = BeautifulSoup(response.render().content, "html.parser")
        assert bool(soup.find("th", text="ID")) is expected

    @pytest.mark.parametrize(("include_index_column", "expected"), [(True, True), (False, False)])
    def it_displays_index_column_when_include_index_column_is_true(rf, include_index_column, expected):
        request = rf.get("/")
        view = TestHxView
        view.include_index_column = include_index_column
        response = view.as_view()(request)
        soup = BeautifulSoup(response.render().content, "html.parser")
        assert bool(soup.findAll("span", {"x-text": "index"})) is expected


class FiltersetWithTabs(TestFilterset):
    tabs_filter = TabFilter(
        choices=[("active", "Active"), ("inactive", "Inactive")],
        method="filter_by_status",
        empty_label=None,
    )

    def filter_by_status(self, queryset, name, value):
        if value == "active":
            return queryset.filter(is_active=True)
        elif value == "inactive":
            return queryset.filter(is_active=False)
        return queryset


class TestHxViewWithTabs(TestHxView):
    filterset_class = FiltersetWithTabs


def describe_disable_zero_count_tabs():
    def it_defaults_to_true():
        assert GenericFilterListViewHX.disable_zero_count_tabs is True

    def it_renders_disable_zero_count_tabs_script_when_enabled(rf):
        request = rf.get("/")
        view = TestHxViewWithTabs
        view.disable_zero_count_tabs = True
        response = view.as_view()(request)
        soup = BeautifulSoup(response.render().content, "html.parser")
        scripts = soup.find_all("script")
        script_texts = [s.string for s in scripts if s.string]
        assert any("disableZeroCountTabs" in text for text in script_texts)

    def it_does_not_render_disable_zero_count_tabs_script_when_disabled(rf):
        request = rf.get("/")
        view = TestHxViewWithTabs
        view.disable_zero_count_tabs = False
        response = view.as_view()(request)
        soup = BeautifulSoup(response.render().content, "html.parser")
        scripts = soup.find_all("script")
        script_texts = [s.string for s in scripts if s.string]
        assert not any("disableZeroCountTabs" in text for text in script_texts)

    def it_adds_hx_on_after_settle_to_filter_counts_trigger_when_enabled(rf):
        request = rf.get("/")
        view = TestHxViewWithTabs
        view.disable_zero_count_tabs = True
        response = view.as_view()(request)
        soup = BeautifulSoup(response.render().content, "html.parser")
        filter_counts_trigger = soup.find(attrs={"hx-on::after-settle": True})
        assert filter_counts_trigger is not None
        attr_value = filter_counts_trigger.get("hx-on::after-settle", "")
        assert "disableZeroCountTabs()" in str(attr_value)

    def it_does_not_add_hx_on_after_settle_when_disabled(rf):
        request = rf.get("/")
        view = TestHxViewWithTabs
        view.disable_zero_count_tabs = False
        response = view.as_view()(request)
        soup = BeautifulSoup(response.render().content, "html.parser")
        # Find all elements with hx-on::after-settle attribute
        elements_with_after_settle = soup.find_all(attrs={"hx-on::after-settle": True})
        # None should contain disableZeroCountTabs
        for el in elements_with_after_settle:
            attr_value = el.get("hx-on::after-settle", "")
            assert "disableZeroCountTabs" not in str(attr_value)
