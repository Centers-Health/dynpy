import pytest
from django.db.models import F
from django.http import HttpRequest, QueryDict
from dynpy_gfl import constants
from dynpy_gfl.enums import FilterListOrder
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.ordering import OrderHelper

pytestmark = pytest.mark.django_db


"""
Fixtures
"""


@pytest.fixture
def dummy_user_filter(django_user_model):
    class DummyUserFilter(GenericFilterSet):
        order_by_overrides_attr = None  # For testing purposes so can be overridden

        @property
        def order_by_overrides(self) -> dict:
            return self.order_by_overrides_attr or {"last_name": ["first_name", "last_name"]}

        class Meta:
            model = django_user_model
            fields = ["email", "username", "first_name", "last_name"]

    return DummyUserFilter


@pytest.fixture
def test_users(django_user_model):
    user_4_B_B_B = django_user_model.objects.create(
        username="4", first_name="B", last_name="B", email="B"
    )
    user_3_B_A_A = django_user_model.objects.create(
        username="3", first_name="B", last_name="A", email="A"
    )
    user_2_A_A_D = django_user_model.objects.create(
        username="2", first_name="A", last_name="A", email="D"
    )
    user_1_A_B_C = django_user_model.objects.create(
        username="1", first_name="A", last_name="B", email="C"
    )
    return (user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C)


"""
Tests
"""


def test_by_default_sorts_on_first_column_field_asc(dummy_user_filter, test_users):
    """
    Test that the default sorting is by the first column field ascending

    In this case it should use 'username'
    """

    class DummyUserFilterWithColumns(dummy_user_filter):
        columns = ["username", "email", "first_name", "last_name"]

    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    sorted_qs = DummyUserFilterWithColumns().qs
    assert sorted_qs[0] == user_1_A_B_C
    assert sorted_qs[1] == user_2_A_A_D
    assert sorted_qs[2] == user_3_B_A_A
    assert sorted_qs[3] == user_4_B_B_B


def test_default_sorting_ignores_empty_column_name(dummy_user_filter, test_users):
    """
    Test that the default sorting is by the first column field that is not an empty string

    In this case it should use 'email'
    """

    class DummyUserFilterWithColumns(dummy_user_filter):
        columns = ["", "email", "first_name", "last_name"]

    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    sorted_qs = DummyUserFilterWithColumns().qs
    assert sorted_qs[0] == user_3_B_A_A
    assert sorted_qs[1] == user_4_B_B_B
    assert sorted_qs[2] == user_1_A_B_C
    assert sorted_qs[3] == user_2_A_A_D


def test_sorts_on_first_field_asc_if_no_columns(dummy_user_filter, test_users):
    """
    Test that it sorts by Meta field ascending if no columns

    In this case it should use 'email'
    """
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    sorted_qs = dummy_user_filter().qs
    assert sorted_qs[0] == user_3_B_A_A
    assert sorted_qs[1] == user_4_B_B_B
    assert sorted_qs[2] == user_1_A_B_C
    assert sorted_qs[3] == user_2_A_A_D


def test_it_can_sort_by_single_default_order_field(dummy_user_filter, test_users):
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    duf = dummy_user_filter()
    duf.default_order_fields = ["username"]
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_1_A_B_C
    assert sorted_qs[1] == user_2_A_A_D
    assert sorted_qs[2] == user_3_B_A_A
    assert sorted_qs[3] == user_4_B_B_B


def test_it_can_sort_by_multiple_default_order_fields(dummy_user_filter, test_users):
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    duf = dummy_user_filter()
    duf.default_order_fields = ["first_name", "last_name"]
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_2_A_A_D
    assert sorted_qs[1] == user_1_A_B_C
    assert sorted_qs[2] == user_3_B_A_A
    assert sorted_qs[3] == user_4_B_B_B


def test_it_can_reverse_sort_by_single_default_order_field(dummy_user_filter, test_users):
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    duf = dummy_user_filter()
    duf.default_order_fields = ["username"]
    duf.default_order = FilterListOrder.DESC
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_4_B_B_B
    assert sorted_qs[1] == user_3_B_A_A
    assert sorted_qs[2] == user_2_A_A_D
    assert sorted_qs[3] == user_1_A_B_C


def test_it_can_reverse_sort_by_multiple_default_order_fields(dummy_user_filter, test_users):
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    duf = dummy_user_filter()
    duf.default_order_fields = ["first_name", "last_name"]
    duf.default_order = FilterListOrder.DESC
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_4_B_B_B
    assert sorted_qs[1] == user_3_B_A_A
    assert sorted_qs[2] == user_1_A_B_C
    assert sorted_qs[3] == user_2_A_A_D


def test_it_can_sort_by_multiple_default_order_fields_asc_then_desc(dummy_user_filter, test_users):
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    duf = dummy_user_filter()
    duf.default_order_fields = ["first_name", "-last_name"]
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_1_A_B_C
    assert sorted_qs[1] == user_2_A_A_D
    assert sorted_qs[2] == user_4_B_B_B
    assert sorted_qs[3] == user_3_B_A_A


def test_it_can_sort_by_multiple_default_order_fields_desc_then_asc(dummy_user_filter, test_users):
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    duf = dummy_user_filter()
    duf.default_order_fields = ["-first_name", "last_name"]
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_3_B_A_A
    assert sorted_qs[1] == user_4_B_B_B
    assert sorted_qs[2] == user_2_A_A_D
    assert sorted_qs[3] == user_1_A_B_C


def test_ignores_default_order_if_default_field_is_ordered(dummy_user_filter, test_users):
    """
    If any of the default_order_fields are ordered (i.e. have a "-" at the beginning to indicate it should
    be reverse sorted), then default_order is ignored *for all fields* on initial page load. Fields without
    a "-" are ordered DESC and fields with are ordered ASC
    """
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    duf = dummy_user_filter()
    duf.default_order_fields = ["-first_name", "last_name"]
    duf.default_order = FilterListOrder.DESC
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_3_B_A_A
    assert sorted_qs[1] == user_4_B_B_B
    assert sorted_qs[2] == user_2_A_A_D
    assert sorted_qs[3] == user_1_A_B_C


def test_it_uses_request_ordering_when_there_is_a_request(dummy_user_filter, test_users):
    """
    Test that request parameters 'order_by' and 'order' override all defaults
    """
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    fake_request = HttpRequest()
    fake_request.GET = QueryDict("order_by=username&order=DESC")
    duf = dummy_user_filter()
    duf.default_order_fields = ["first_name", "last_name"]
    duf.default_order = FilterListOrder.ASC
    duf.request = fake_request
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_4_B_B_B
    assert sorted_qs[1] == user_3_B_A_A
    assert sorted_qs[2] == user_2_A_A_D
    assert sorted_qs[3] == user_1_A_B_C


def test_order_by_overrides_are_used(dummy_user_filter, test_users):
    """
    Test that request parameters 'order_by' and 'order' override all defaults
    """
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    fake_request = HttpRequest()
    fake_request.GET = QueryDict("order_by=last_name&order=ASC")
    duf = dummy_user_filter()
    duf.request = fake_request
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_2_A_A_D
    assert sorted_qs[1] == user_1_A_B_C
    assert sorted_qs[2] == user_3_B_A_A
    assert sorted_qs[3] == user_4_B_B_B


def test_order_by_overrides_invert_when_order_is_desc(dummy_user_filter, test_users):
    """
    Test that request parameters 'order_by' and 'order' override all defaults
    """
    user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
    fake_request = HttpRequest()
    fake_request.GET = QueryDict("order_by=last_name&order=DESC")
    duf = dummy_user_filter()
    duf.request = fake_request
    sorted_qs = duf.qs
    assert sorted_qs[0] == user_4_B_B_B
    assert sorted_qs[1] == user_3_B_A_A
    assert sorted_qs[2] == user_1_A_B_C
    assert sorted_qs[3] == user_2_A_A_D


@pytest.mark.parametrize(
    ("field", "column_definition"),
    [
        (
            "first_name",
            {"allow_ordering": True, "field_name": "first_name", "label": "First Name"},
        ),
        (
            ("first_name", "Custom Label"),
            {"allow_ordering": True, "field_name": "first_name", "label": "Custom Label"},
        ),
        (
            ("first_name", "Custom Label", False),
            {"allow_ordering": False, "field_name": "first_name", "label": "Custom Label"},
        ),
    ],
)
def test_field_to_column_definition(field, column_definition, dummy_user_filter):
    duf = dummy_user_filter()
    assert duf.field_to_column_definition(field) == column_definition


@pytest.mark.parametrize(
    ("field", "error_message"),
    [
        (
            (1, "Custom Label"),
            "Field definition of type tuple must have a string at index 0. It has a int.",
        ),
        (
            (True, "Custom Label"),
            "Field definition of type tuple must have a string at index 0. It has a bool.",
        ),
        (
            (None, "Custom Label"),
            "Field definition of type tuple must have a string at index 0. It has a NoneType.",
        ),
        (
            ("field_name", 1),
            "Field definition of type tuple must have a string at index 1. It has a int.",
        ),
        (
            ("field_name", True),
            "Field definition of type tuple must have a string at index 1. It has a bool.",
        ),
        (
            ("field_name", None),
            "Field definition of type tuple must have a string at index 1. It has a NoneType.",
        ),
        (
            ("field_name", "Custom Label", None),
            "Field definition of type tuple with 3 values must have a bool at index 2. It has a NoneType.",
        ),
        (
            1,
            "Field definition must be either a string or a tuple. It is of type int.",
        ),
        (
            True,
            "Field definition must be either a string or a tuple. It is of type bool.",
        ),
    ],
)
def test_field_to_column_definition_raises_errors(field, error_message, dummy_user_filter):
    duf = dummy_user_filter()
    with pytest.raises(Exception, match=error_message):
        duf.field_to_column_definition(field)


def describe_is_filtered():
    def it_is_filtered_when_params_overlap_filter_fields(dummy_user_filter):
        assert dummy_user_filter().is_filtered({"username": "bob"}) is True

    def it_is_NOT_filtered_when_data_does_not_overlap_filter_fields(dummy_user_filter):
        """Data comes from the GET Params"""
        assert dummy_user_filter().is_filtered({"test": "bob"}) is False

    @pytest.mark.parametrize(
        ("suffix", "expected"),
        [("min", True), ("max", True), ("before", True), ("after", True), ("test", False)],
    )
    def it_matches_range_filters(rf, dummy_user_filter, suffix, expected):
        """Range filters add min|max|after|before to the filter name"""
        assert dummy_user_filter().is_filtered({f"username_{suffix}": "bob"}) is expected


def describe_default_filters():
    def they_are_applied_when_the_filterset_is_not_filtered(dummy_user_filter):
        dummy_user_filter.get_default_filters = lambda self, request: {"username": "bob"}
        duf = dummy_user_filter()
        assert duf.data["username"] == "bob"

    def they_are_NOT_applied_when_the_filterset_is_filtered(dummy_user_filter):
        dummy_user_filter.get_default_filters = lambda self, request: {"username": "bob"}
        duf = dummy_user_filter({"email": "dave"})
        assert duf.data.get("username", None) is None


def test_processes_dash_on_page_load_ordering(dummy_user_filter, django_user_model):
    """
    When a default order field contains a '-' it should be sorted descending
    """
    user_1 = django_user_model.objects.create(username="1", first_name="A", last_name="A")
    user_2 = django_user_model.objects.create(username="2", first_name="B", last_name="B")
    user_3 = django_user_model.objects.create(username="3", first_name="C", last_name="C")

    fake_request = HttpRequest()
    fake_request.GET = QueryDict()
    duf = dummy_user_filter()
    duf.default_order_fields = ["-last_name"]
    duf.request = fake_request
    sorted_qs = duf.qs

    assert sorted_qs[0] == user_3
    assert sorted_qs[1] == user_2
    assert sorted_qs[2] == user_1


def describe_ordering_with_overrides():
    def test_order_by_overrides_are_used(dummy_user_filter, test_users):
        """
        Test that request parameters 'order_by' and 'order' override all defaults
        """
        user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
        fake_request = HttpRequest()
        fake_request.GET = QueryDict("order_by=last_name&order=ASC")
        duf = dummy_user_filter()
        duf.request = fake_request
        sorted_qs = duf.qs
        assert sorted_qs[0] == user_2_A_A_D
        assert sorted_qs[1] == user_1_A_B_C
        assert sorted_qs[2] == user_3_B_A_A
        assert sorted_qs[3] == user_4_B_B_B

    def test_order_by_overrides_invert_when_order_is_desc(dummy_user_filter, test_users):
        """
        Test that request parameters 'order_by' and 'order' override all defaults
        """
        user_4_B_B_B, user_3_B_A_A, user_2_A_A_D, user_1_A_B_C = test_users
        fake_request = HttpRequest()
        fake_request.GET = QueryDict("order_by=last_name&order=DESC")
        duf = dummy_user_filter()
        duf.request = fake_request
        sorted_qs = duf.qs
        assert sorted_qs[0] == user_4_B_B_B
        assert sorted_qs[1] == user_3_B_A_A
        assert sorted_qs[2] == user_1_A_B_C
        assert sorted_qs[3] == user_2_A_A_D

    def test_can_override_with_dict(dummy_user_filter, django_user_model):
        """
        Swap asc with desc for test purposes
        """
        user_1 = django_user_model.objects.create(username="1", first_name="A", last_name="A")
        user_2 = django_user_model.objects.create(username="2", first_name="B", last_name="B")
        user_3 = django_user_model.objects.create(username="3", first_name="C", last_name="C")

        fake_request = HttpRequest()
        fake_request.GET = QueryDict("order_by=last_name&order=DESC")
        duf = dummy_user_filter()
        duf.order_by_overrides_attr = {
            "last_name": {constants.DESC: F("last_name").asc(), constants.ASC: F("last_name").desc()}
        }
        duf.request = fake_request
        sorted_qs = duf.qs

        # Should be ASC even though query string says Desc bec of the override
        assert sorted_qs[0] == user_1
        assert sorted_qs[1] == user_2
        assert sorted_qs[2] == user_3

    def test_can_override_with_list_with_dict(dummy_user_filter, django_user_model):
        user_1 = django_user_model.objects.create(username="1", first_name="A", last_name="A")
        user_2 = django_user_model.objects.create(username="2", first_name="B", last_name="A")
        user_3 = django_user_model.objects.create(username="3", first_name="C", last_name="C")

        fake_request = HttpRequest()
        fake_request.GET = QueryDict("order_by=last_name&order=DESC")
        duf = dummy_user_filter()
        duf.order_by_overrides_attr = {
            "last_name": [
                {constants.DESC: F("last_name").asc(), constants.ASC: F("last_name").desc()},
                "first_name",
            ]
        }
        duf.request = fake_request
        sorted_qs = duf.qs

        # Same as previous test (ASC instead of DESC) however, because also overriding using first name
        # user 2 comes first because first name is still sorting DESC (following the query string)
        assert sorted_qs[0] == user_2
        assert sorted_qs[1] == user_1
        assert sorted_qs[2] == user_3

    def test_can_override_with_OrderHelper_dataclass(dummy_user_filter, django_user_model):
        """
        Swap asc with desc for test purposes
        """
        user_1 = django_user_model.objects.create(username="1", first_name="A", last_name="A")
        user_2 = django_user_model.objects.create(username="2", first_name="B", last_name="B")
        user_3 = django_user_model.objects.create(username="3", first_name="C", last_name="C")

        fake_request = HttpRequest()
        fake_request.GET = QueryDict("order_by=last_name&order=DESC")
        duf = dummy_user_filter()
        duf.order_by_overrides_attr = {
            "last_name": OrderHelper(ASC=F("last_name").desc(), DESC=F("last_name").asc())
        }
        duf.request = fake_request
        sorted_qs = duf.qs

        # Should be ASC even though query string says Desc bec of the override
        assert sorted_qs[0] == user_1
        assert sorted_qs[1] == user_2
        assert sorted_qs[2] == user_3


def test_invalid_field_in_order_by_does_not_cause_error(dummy_user_filter, test_users):
    fake_request = HttpRequest()
    fake_request.GET = QueryDict("order_by=invalid_field&order=ASC")
    duf = dummy_user_filter()
    duf.request = fake_request
    sorted_qs = duf.qs
    assert sorted_qs


@pytest.mark.parametrize(
    "default_order_fields",
    [
        "invalid_field",
        ["invalid_field"],
        ["first_name", "invalid_field"],
    ],
)
def test_invalid_field_in_default_order_fields_raises_error(
    dummy_user_filter, test_users, default_order_fields
):
    fake_request = HttpRequest()
    fake_request.GET = QueryDict()
    duf = dummy_user_filter
    duf.request = fake_request
    duf.default_order_fields = default_order_fields
    with pytest.raises(ValueError, match="invalid_field"):
        duf()
