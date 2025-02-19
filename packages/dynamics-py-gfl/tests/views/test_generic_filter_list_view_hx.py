from typing import Any

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
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
