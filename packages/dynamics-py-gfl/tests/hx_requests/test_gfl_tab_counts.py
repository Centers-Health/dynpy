import pytest
from django.contrib.auth import get_user_model

from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.hx_requests import GflTabCounts
from dynpy_gfl.views import GenericFilterListViewHX
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
    has_tabs = True

    def filter_qs_by_tab(self, qs, tab):
        if tab == "1":
            return qs.filter(username__contains="1")
        elif tab == "2":
            return qs.filter(username__contains="2")
        return qs


@pytest.fixture(autouse=True)
def _create_test_users():
    get_user_model().objects.create(username="test_user1", first_name="Test", last_name="User")
    get_user_model().objects.create(username="test_user11", first_name="Test", last_name="User3")
    get_user_model().objects.create(username="test_user2", first_name="Test", last_name="User2")


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("tab", "expected_count"),
    [
        ("1", "2"),
        ("2", "1"),
    ],
)
def test_tabs_count_filters_using_filter_qs_by_tab_from_view(tab, expected_count):
    response = hx_get(
        GflTabCounts,
        TestHxView,
        get_params={"tab": tab},
    )
    assert response.content.decode() == expected_count


@pytest.mark.django_db()
def test_tabs_count_ignores_active_tab():
    """
    If it is not removed from the GET params, it will be passed
    to the view and filter down the tabs count by the active tab
    which means the count will always be 0 because it will be filtering
    by both the tab its doing the count on and the active tab.
    """
    response = hx_get(
        GflTabCounts,
        TestHxView,
        get_params={"tab": "1", "active_tab": "2"},
    )
    assert response.content.decode() == "2"
