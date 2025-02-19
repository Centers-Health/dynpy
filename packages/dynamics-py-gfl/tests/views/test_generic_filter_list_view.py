from copy import deepcopy

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.forms import ModelForm

from dynpy_gfl.constants import DEFAULT_ARG
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.views import GenericFilterListView

pytestmark = pytest.mark.django_db


"""
Helpers
"""


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "is_active",
        ]


class UserFilterset(GenericFilterSet):
    columns = ["username", "first_name", "last_name"]
    extra_filters = ["username"]

    class Meta:
        fields = ["username", "first_name", "last_name"]
        model = get_user_model()


class UserListView(GenericFilterListView):
    base_template = "tests/dummy_base.html"

    filterset_class = UserFilterset


"""
Fixtures
"""


@pytest.fixture
def create_generic_filter_list_class(django_user_model):
    def _create_generic_filter_list_class(fields=DEFAULT_ARG, skip_model=False, columns=DEFAULT_ARG):

        f = fields if fields != DEFAULT_ARG else []
        m = django_user_model if not skip_model else None
        qs = django_user_model.objects.all() if not skip_model else None
        c = columns if columns != DEFAULT_ARG else []

        class TestFilterset(GenericFilterSet):
            columns = c

            class Meta:
                fields = f
                model = m

        # SETUP FOR TESTING ACTION RENDERING/HANDLING:

        class SomeGenericView(GenericFilterListView):
            queryset = qs
            filterset_class = TestFilterset

        return deepcopy(SomeGenericView())

    return _create_generic_filter_list_class


""" Tests """


def test_that_paginate_by_is_overridden_by_get_value(rf, create_generic_filter_list_class):
    G = create_generic_filter_list_class()
    test_value = str(G.paginate_by + 1)
    request = rf.get(f"testurl?paginate_by={test_value}")
    G.setup(request)
    assert G.paginate_by == test_value


@pytest.mark.parametrize(
    "columns,fields,expected",
    [
        (
            None,
            ["first_name", "last_name"],
            [
                {"field_name": "first_name", "label": "First Name", "allow_ordering": True},
                {"field_name": "last_name", "label": "Last Name", "allow_ordering": True},
            ],
        ),
        (
            None,
            {"first_name": [], "last_name": []},
            [
                {"field_name": "first_name", "label": "First Name", "allow_ordering": True},
                {"field_name": "last_name", "label": "Last Name", "allow_ordering": True},
            ],
        ),
        (
            ["first_name", "last_name"],
            ["first_name", "last_name", "is_active"],
            [
                {"field_name": "first_name", "label": "First Name", "allow_ordering": True},
                {"field_name": "last_name", "label": "Last Name", "allow_ordering": True},
            ],
        ),
        (
            [
                ("first_name", "Custom First Name Label"),
                ("last_name", "Custom Last Name Label"),
            ],
            ["first_name", "last_name"],
            [
                {"field_name": "first_name", "label": "Custom First Name Label", "allow_ordering": True},
                {"field_name": "last_name", "label": "Custom Last Name Label", "allow_ordering": True},
            ],
        ),
        (
            [
                ("first_name", "Custom First Name Label", False),
                ("last_name", "Custom Last Name Label", True),
            ],
            ["first_name", "last_name"],
            [
                {
                    "field_name": "first_name",
                    "label": "Custom First Name Label",
                    "allow_ordering": False,
                },
                {"field_name": "last_name", "label": "Custom Last Name Label", "allow_ordering": True},
            ],
        ),
    ],
)
def test_get_columns(columns, fields, expected, create_generic_filter_list_class):
    G = create_generic_filter_list_class(fields=fields, columns=columns)

    assert G.get_columns() == expected


@pytest.mark.parametrize(
    "fields,columns,error_message",
    [
        (
            ["first_name"],
            [(None, "First Name")],
            "Field definition of type tuple must have a string at index 0. It has a NoneType.",
        ),
        (
            ["first_name"],
            [("first_name", None)],
            "Field definition of type tuple must have a string at index 1. It has a NoneType.",
        ),
        (
            ["first_name"],
            [(None, None)],
            "Field definition of type tuple must have a string at index 0. It has a NoneType.",
        ),
        (
            ["first_name"],
            [("first_name", "First Name", None)],
            "Field definition of type tuple with 3 values must have a bool at index 2. It has a NoneType.",
        ),
    ],
)
def test_get_columns_with_bad_column_inputs(
    fields, columns, error_message, create_generic_filter_list_class
):
    G = create_generic_filter_list_class(fields=fields, columns=columns)

    with pytest.raises(Exception) as e:
        G.get_columns()
    assert str(e.value) == error_message


def test_object_name_is_the_models_verbose_plural_name(
    create_generic_filter_list_class, django_user_model
):
    G = create_generic_filter_list_class()
    assert G.object_name.lower() == django_user_model.Meta.verbose_name_plural


def describe_freezing_columns():
    """Describe freezing columns"""

    def that_it_does_not_freeze_any_columns_by_default(create_generic_filter_list_class):
        """Test that it does not freeze any columns by default"""
        G = create_generic_filter_list_class()
        assert G.get_freeze_columns() == 0

    def that_frozen_column_count_can_be_set_with_property():
        class SomeGenericView(GenericFilterListView):
            freeze_columns = 2

        G = SomeGenericView()
        assert len(G.get_frozen_column_range) == 2

    def that_frozen_column_count_can_be_set_dynamically():
        class SomeGenericView(GenericFilterListView):
            def get_freeze_columns(self):
                return 2

        G = SomeGenericView()
        assert len(G.get_frozen_column_range) == 2

    def describe_get_frozen_column_range():
        """Describe get frozen column range"""

        def it_should_return_range_starting_with_1(create_generic_filter_list_class):
            """Test that it marks frozen the correct number of columns"""
            G = create_generic_filter_list_class()
            G.freeze_columns = 3
            assert G.get_frozen_column_range[0] == 1

        def it_should_return_range_that_ends_with_freeze_columns(create_generic_filter_list_class):
            G = create_generic_filter_list_class()
            G.freeze_columns = 3
            assert G.get_frozen_column_range[-1] == G.freeze_columns

        def the_range_should_have_the_proper_number_of_values(create_generic_filter_list_class):
            G = create_generic_filter_list_class()
            G.freeze_columns = 3
            assert len(G.get_frozen_column_range) == G.freeze_columns


def describe_extra_filters():
    def it_hides_extra_filters_by_default(rf):
        request = rf.get("/")
        response = UserListView.as_view()(request)
        soup = BeautifulSoup(response.render().content, features="html.parser")
        extra_filters = soup.find("div", {"id": "extraFilters"})

        assert "show" not in extra_filters.attrs.get("class")

    def it_displays_extra_filters_when_show_extra_filters_is_true(rf):
        request = rf.get("/?show_extra_filters=true")
        response = UserListView.as_view()(request)
        soup = BeautifulSoup(response.render().content, features="html.parser")
        extra_filters = soup.find("div", {"id": "extraFilters"})

        assert "show" in extra_filters.attrs.get("class")
        assert extra_filters.find("input", {"name": "username"})
