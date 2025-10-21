import pytest
from django.forms import Form
from dynpy_forms.fields import GroupAwareModelMultipleChoiceField
from tests.models import Publisher


class DummyForm(Form):
    publishers = GroupAwareModelMultipleChoiceField(
        queryset=Publisher.objects.all(),
        group_by_field="location__name",
        filter_name="publishers",
    )


@pytest.fixture
def locations_and_publishers(db):
    """Create test data with publishers grouped by location"""
    from tests.models import Location

    ny = Location.objects.create(name="New York")
    la = Location.objects.create(name="Los Angeles")
    chi = Location.objects.create(name="Chicago")

    penguin = Publisher.objects.create(name="Penguin", location=ny)
    random_house = Publisher.objects.create(name="Random House", location=ny)
    harpercollins = Publisher.objects.create(name="HarperCollins", location=la)
    simon = Publisher.objects.create(name="Simon & Schuster", location=chi)

    return {
        "locations": {"ny": ny, "la": la, "chi": chi},
        "publishers": {
            "penguin": penguin,
            "random_house": random_house,
            "harpercollins": harpercollins,
            "simon": simon,
        },
    }


def describe_initialization():
    def it_requires_group_by_field():
        with pytest.raises(ValueError, match="`group_by_field` is required"):
            GroupAwareModelMultipleChoiceField(
                queryset=Publisher.objects.all(),
                filter_name="publishers",
            )

    def it_requires_filter_name():
        with pytest.raises(ValueError, match="`filter_name` is required"):
            GroupAwareModelMultipleChoiceField(
                queryset=Publisher.objects.all(),
                group_by_field="location__name",
            )

    def it_sets_group_key_from_prefix_and_filter_name():
        field = GroupAwareModelMultipleChoiceField(
            queryset=Publisher.objects.all(),
            group_by_field="location__name",
            filter_name="publishers",
        )
        assert field.group_key == "_group_publishers"

    def it_uses_custom_group_prefix():
        field = GroupAwareModelMultipleChoiceField(
            queryset=Publisher.objects.all(),
            group_by_field="location__name",
            filter_name="publishers",
            group_prefix="_custom_",
        )
        assert field.group_key == "_custom_publishers"


def describe_widget_attrs():
    def it_adds_group_key_and_prefix_data_attributes():
        field = GroupAwareModelMultipleChoiceField(
            queryset=Publisher.objects.all(),
            group_by_field="location__name",
            filter_name="publishers",
        )
        attrs = field.widget_attrs(field.widget)
        assert attrs["data-group-key"] == "_group_publishers"
        assert attrs["data-group-prefix"] == "_group_"


def describe_clean_method():
    def it_returns_normal_values_when_no_group_values_in_request(locations_and_publishers, rf):
        publishers = locations_and_publishers["publishers"]
        penguin = publishers["penguin"]
        simon = publishers["simon"]

        request = rf.get("/", {"publishers": [str(penguin.pk), str(simon.pk)]})
        field = GroupAwareModelMultipleChoiceField(
            queryset=Publisher.objects.all(),
            group_by_field="location__name",
            filter_name="publishers",
            request=request,
        )

        cleaned = field.clean([str(penguin.pk), str(simon.pk)])
        assert len(cleaned) == 2
        assert penguin in cleaned
        assert simon in cleaned

    def it_expands_group_tokens_from_request(locations_and_publishers, rf):
        publishers = locations_and_publishers["publishers"]
        penguin = publishers["penguin"]
        random_house = publishers["random_house"]

        # Group token for New York publishers in request
        request = rf.get("/", {"_group_publishers": ["New York"]})
        field = GroupAwareModelMultipleChoiceField(
            queryset=Publisher.objects.all(),
            group_by_field="location__name",
            filter_name="publishers",
            request=request,
        )

        # Pass group prefix token in value
        cleaned = field.clean(["_group_publishers:New York"])
        assert len(cleaned) == 2
        assert penguin in cleaned
        assert random_house in cleaned

    def it_combines_normal_and_group_values(locations_and_publishers, rf):
        publishers = locations_and_publishers["publishers"]
        penguin = publishers["penguin"]
        random_house = publishers["random_house"]
        simon = publishers["simon"]

        # Group token for New York + individual Chicago publisher
        request = rf.get(
            "/",
            {
                "_group_publishers": ["New York"],
                "publishers": [str(simon.pk)],
            },
        )
        field = GroupAwareModelMultipleChoiceField(
            queryset=Publisher.objects.all(),
            group_by_field="location__name",
            filter_name="publishers",
            request=request,
        )

        cleaned = field.clean([str(simon.pk), "_group_publishers:New York"])
        assert len(cleaned) == 3
        assert penguin in cleaned
        assert random_house in cleaned
        assert simon in cleaned

    def it_handles_multiple_group_tokens(locations_and_publishers, rf):
        publishers = locations_and_publishers["publishers"]
        penguin = publishers["penguin"]
        random_house = publishers["random_house"]
        simon = publishers["simon"]

        # Group tokens for New York and Chicago
        request = rf.get("/", {"_group_publishers": ["New York", "Chicago"]})
        field = GroupAwareModelMultipleChoiceField(
            queryset=Publisher.objects.all(),
            group_by_field="location__name",
            filter_name="publishers",
            request=request,
        )

        cleaned = field.clean(["_group_publishers:New York", "_group_publishers:Chicago"])
        assert len(cleaned) == 3
        assert penguin in cleaned
        assert random_house in cleaned
        assert simon in cleaned

    def it_returns_empty_list_when_no_values(locations_and_publishers, rf):
        request = rf.get("/", {})
        field = GroupAwareModelMultipleChoiceField(
            queryset=Publisher.objects.all(),
            group_by_field="location__name",
            filter_name="publishers",
            request=request,
            required=False,
        )

        cleaned = field.clean([])
        assert not cleaned

    def it_handles_none_request(locations_and_publishers):
        publishers = locations_and_publishers["publishers"]
        penguin = publishers["penguin"]

        field = GroupAwareModelMultipleChoiceField(
            queryset=Publisher.objects.all(),
            group_by_field="location__name",
            filter_name="publishers",
            request=None,
        )

        # Without request, group values won't be expanded
        cleaned = field.clean([str(penguin.pk)])
        assert len(cleaned) == 1
        assert penguin in cleaned
