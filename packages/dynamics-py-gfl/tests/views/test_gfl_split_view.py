import pytest
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.views import GFLSplitView


class TestFilterset(GenericFilterSet):
    columns = ["username"]

    class Meta:
        fields = ["username"]
        model = get_user_model()


class TestSplitView(GFLSplitView):
    side_panel_template = "tests/dummy_gfl_side_panel.html"
    base_template = "tests/dummy_base.html"

    filterset_class = TestFilterset


def test_returns_side_panel_template_if_GET_has_split_view_obj_and_fetch_side_panel(rf, test_user):
    request = rf.get(f"/?split_view_obj={test_user.pk}&fetch_side_panel=true")
    response = TestSplitView.as_view()(request)

    assert response.template_name == TestSplitView.side_panel_template
    assert str(test_user) in str(response.render().content)


def test_renders_side_panel_template_if_split_view_obj_in_GET(rf, test_user):
    request = rf.get(f"/?split_view_obj={test_user.pk}")
    response = TestSplitView.as_view()(request)

    # There is list of template names that also includes the filter templates
    assert TestSplitView.template_name in response.template_name
    assert str(test_user) in str(response.render().content)


@pytest.mark.django_db
def test_if_open_by_default_is_false_and_NO_object_side_panel_is_hidden(rf):
    request = rf.get("/")
    TestSplitView.is_open_by_default = False
    response = TestSplitView.as_view()(request)
    soup = BeautifulSoup(response.render().content, features="html.parser")
    assert "d-none" in str(soup.select_one("#side_panel_wrapper").attrs["class"])


@pytest.mark.django_db
def test_if_open_by_default_is_false_and_HAS_object_side_panel_is_visible(rf, test_user):
    request = rf.get(f"/?split_view_obj={test_user.pk}")
    TestSplitView.is_open_by_default = False
    response = TestSplitView.as_view()(request)
    soup = BeautifulSoup(response.render().content, features="html.parser")
    assert "d-none" not in str(soup.select_one("#side_panel_wrapper").attrs["class"])
