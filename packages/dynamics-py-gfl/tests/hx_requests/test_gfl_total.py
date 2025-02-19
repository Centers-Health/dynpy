import pytest
from django.contrib.auth import get_user_model
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.hx_requests import GflTotal
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


@pytest.mark.django_db
def test_count_of_view_is_returned(django_user_model):
    django_user_model.objects.create(username="test_user1", first_name="Test", last_name="User")
    django_user_model.objects.create(username="test_user11", first_name="Test", last_name="User3")
    django_user_model.objects.create(username="test_user2", first_name="Test", last_name="User2")
    response = hx_get(
        GflTotal,
        TestHxView,
    )
    assert response.content.decode() == "3 Users"
