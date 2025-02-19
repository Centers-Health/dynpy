import pytest
from dynpy_gfl import constants
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.templatetags.generic_filter_list_tags import column_header_link
from dynpy_gfl.utils import reverse_asc_desc_order


@pytest.fixture
def test_filter_set(django_user_model):
    class UserFilterSet(GenericFilterSet):
        class Meta:
            model = django_user_model
            fields = ["email", "username", "first_name", "last_name"]

    return UserFilterSet


def test_link_order_is_flipped_on_order_by_column_on_initial_load(rf, test_filter_set):
    """
    Test it flips the default order on the default order_by column
    on initial page load when there is no order_by or order information in the query string.
    GenericFilterSet orders by the first filter field ascending by default which is email in this case
    """
    context = {}
    context["request"] = rf.get("/")
    context["filter"] = test_filter_set(request=context["request"])
    context["column"] = {"field_name": "email", "allow_ordering": True}
    elem = column_header_link(context)
    assert "order=DESC" in elem


def test_link_order_is_not_flipped_for_other_columns_on_initial_load(rf, test_filter_set):
    """
    Test it does not flip the order columns that are not currently being ordered by
    on initial page load when there is no order_by or order information in the query string.
    GenericFilterSet orders by the first filter field ascending by default which is email in this case
    """
    context = {}
    context["request"] = rf.get("/")
    context["filter"] = test_filter_set(request=context["request"])
    context["column"] = {"field_name": "username", "allow_ordering": True}
    elem = column_header_link(context)
    assert "order=ASC" in elem


@pytest.mark.parametrize("order", [constants.ASC, constants.DESC])
def test_link_order_is_flipped_on_order_by_column(rf, test_filter_set, order):
    context = {}
    context["request"] = rf.get(f"/?order_by=email&order={order}")
    context["filter"] = test_filter_set(request=context["request"])
    context["column"] = {"field_name": "email", "allow_ordering": True}
    elem = column_header_link(context)
    flipped_order = reverse_asc_desc_order(order)
    assert f"order={flipped_order}" in elem


@pytest.mark.parametrize("order", [constants.ASC, constants.DESC])
def test_link_order_is_flipped_on_order_by_column_when_there_are_order_by_overrides(
    rf, test_filter_set, order
):
    context = {}
    context["request"] = rf.get(f"/?order_by=username&order={order}")
    test_filter_set.order_by_overrides = {"username": ["first_name", "last_name"]}
    context["filter"] = test_filter_set(request=context["request"])
    context["column"] = {"field_name": "username", "allow_ordering": True}
    elem = column_header_link(context)
    flipped_order = reverse_asc_desc_order(order)
    assert f"order={flipped_order}" in elem


@pytest.mark.parametrize("order", [constants.ASC, constants.DESC])
def test_link_order_is_not_flipped_for_other_columns(rf, test_filter_set, order):
    context = {}
    context["request"] = rf.get(f"/?order_by=email&order={order}")
    context["filter"] = test_filter_set(request=context["request"])
    context["column"] = {"field_name": "username", "allow_ordering": True}
    elem = column_header_link(context)
    assert f"order={order}" in elem


@pytest.mark.parametrize(
    ("order", "arrow_direction"),
    [
        (
            constants.ASC,
            "down",
        ),  # sounds counter intuitive but ascending order starts from a at the top and goes down to z
        (constants.DESC, "up"),
    ],
)
def test_displays_arrow_according_to_the_current_order(rf, test_filter_set, order, arrow_direction):
    context = {}
    context["request"] = rf.get(f"/?order_by=email&order={order}")
    context["filter"] = test_filter_set(request=context["request"])
    context["column"] = {"field_name": "email", "allow_ordering": True}
    elem = column_header_link(context)
    assert f"fa-angle-{arrow_direction}" in elem


def test_returns_just_label_when_allow_ordering_is_false(rf, test_filter_set):
    context = {}
    context["request"] = rf.get("/")
    context["filter"] = test_filter_set(request=context["request"])
    context["column"] = {"field_name": "email", "label": "Email", "allow_ordering": False}
    elem = column_header_link(context)
    assert elem == "Email"
