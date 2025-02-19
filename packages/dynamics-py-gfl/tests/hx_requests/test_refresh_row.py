from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.hx_requests import RefreshRow
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


def describe_refresh_row():
    def it_returns_the_row(test_user):
        response = hx_get(RefreshRow, TestHxView, hx_kwargs={"object": test_user})
        soup = BeautifulSoup(response.content, "html.parser")
        assert soup.find("td", text=test_user.username)
        assert soup.find("td", text=test_user.first_name)
        assert soup.find("td", text=test_user.last_name)

    def returns_nothing_if_object_not_in_qs(test_user):
        class NoObjectFilterset(TestFilterset):
            @property
            def qs(self):
                return super().qs.none()

        class NoObjectView(TestHxView):
            filterset_class = NoObjectFilterset

        response = hx_get(RefreshRow, NoObjectView, hx_kwargs={"object": test_user})
        soup = BeautifulSoup(response.content, "html.parser")
        assert not soup.find("td", text=test_user.username)
