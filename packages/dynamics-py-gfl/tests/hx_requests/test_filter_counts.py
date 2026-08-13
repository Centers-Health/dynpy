import pytest
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django_filters import ChoiceFilter
from dynpy_gfl.filters import TabFilter
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.hx_requests import FilterCountsHx
from dynpy_gfl.views import GenericFilterListViewHX
from dynpy_gfl.widgets import InlineButtonRadioSelectWithCounts
from tests.utils import hx_get


class TestFilterset(GenericFilterSet):
    columns = ["username"]

    class Meta:
        fields = ["username"]
        model = get_user_model()


class TestHxView(GenericFilterListViewHX):
    template_name = "tests/dummy_gfl.html"
    filterset_class = TestFilterset
    base_template = "tests/dummy_base.html"


def describe_filter_counts_hx():
    def it_returns_empty_when_no_filters_to_count():
        response = hx_get(FilterCountsHx, TestHxView)
        assert response.content.decode().strip() == ""

    @pytest.mark.django_db
    def it_returns_counts_for_tabs_filter(django_user_model):
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

        class ViewWithTabs(TestHxView):
            filterset_class = FiltersetWithTabs

        django_user_model.objects.create(username="active1", is_active=True)
        django_user_model.objects.create(username="active2", is_active=True)
        django_user_model.objects.create(username="inactive1", is_active=False)

        response = hx_get(FilterCountsHx, ViewWithTabs)
        soup = BeautifulSoup(response.content, "html.parser")

        active_span = soup.find(id="tabs_filter__active__count")
        inactive_span = soup.find(id="tabs_filter__inactive__count")

        assert active_span is not None
        assert active_span.text == "2"
        assert inactive_span is not None
        assert inactive_span.text == "1"

    @pytest.mark.django_db
    @pytest.mark.parametrize("selected_tab", [None, "active", "inactive"])
    def it_does_not_call_view_get_and_preserves_rendered_counts(django_user_model, selected_tab, mocker):
        class FiltersetWithTabs(TestFilterset):
            tabs_filter = TabFilter(
                choices=[("active", "Active"), ("inactive", "Inactive")],
                method="filter_by_status",
                empty_label=None,
            )

            def filter_by_status(self, queryset, name, value):
                if value == "active":
                    return queryset.filter(is_active=True)
                if value == "inactive":
                    return queryset.filter(is_active=False)
                return queryset

        class ViewWithTabs(TestHxView):
            filterset_class = FiltersetWithTabs

        django_user_model.objects.create(username="active1", is_active=True)
        django_user_model.objects.create(username="active2", is_active=True)
        django_user_model.objects.create(username="inactive1", is_active=False)

        get_params = {"tabs_filter": selected_tab} if selected_tab else None
        view_get = mocker.spy(ViewWithTabs, "get")
        response = hx_get(FilterCountsHx, ViewWithTabs, get_params=get_params)

        assert not view_get.called
        assert response.content.decode() == (
            '\n    \n<span hx-swap-oob="true" id="tabs_filter__active__count">2</span>\n'
            '\n\n    \n<span hx-swap-oob="true" id="tabs_filter__inactive__count">1</span>\n\n\n'
        )

    @pytest.mark.django_db
    def it_returns_counts_for_quick_filters(django_user_model):
        class FiltersetWithQuickFilters(TestFilterset):
            quick_filters = ["is_staff"]

            is_staff = ChoiceFilter(
                choices=[("true", "Staff"), ("false", "Non-Staff")],
                method="filter_by_staff",
                widget=InlineButtonRadioSelectWithCounts,
            )

            def filter_by_staff(self, queryset, name, value):
                if value == "true":
                    return queryset.filter(is_staff=True)
                elif value == "false":
                    return queryset.filter(is_staff=False)
                return queryset

        class ViewWithQuickFilters(TestHxView):
            filterset_class = FiltersetWithQuickFilters

        django_user_model.objects.create(username="staff1", is_staff=True)
        django_user_model.objects.create(username="nonstaff1", is_staff=False)
        django_user_model.objects.create(username="nonstaff2", is_staff=False)

        response = hx_get(FilterCountsHx, ViewWithQuickFilters)
        soup = BeautifulSoup(response.content, "html.parser")

        staff_span = soup.find(id="is_staff__true__count")
        nonstaff_span = soup.find(id="is_staff__false__count")

        assert staff_span is not None
        assert staff_span.text == "1"
        assert nonstaff_span is not None
        assert nonstaff_span.text == "2"
