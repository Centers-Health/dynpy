import pytest
from bs4 import BeautifulSoup
from django.forms import Form, ModelMultipleChoiceField
from django.http import QueryDict
from dynpy_forms.widgets import GroupAwareBootstrapMultiSelect
from tests.models import Location, Publisher


@pytest.fixture
def publishers(db):
    """Create test publishers"""

    ny = Location.objects.create(name="New York")
    la = Location.objects.create(name="Los Angeles")

    penguin = Publisher.objects.create(name="Penguin", location=ny)
    random_house = Publisher.objects.create(name="Random House", location=ny)
    harpercollins = Publisher.objects.create(name="HarperCollins", location=la)

    return {
        "penguin": penguin,
        "random_house": random_house,
        "harpercollins": harpercollins,
    }


def describe_initialization():
    def it_adds_group_aware_css_class():
        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_test", "data-group-prefix": "_group_"}
        )
        assert "selectpicker-group-aware" in widget.attrs["class"]

    def it_preserves_existing_css_classes():
        widget = GroupAwareBootstrapMultiSelect(
            attrs={
                "class": "custom-class",
                "data-group-key": "_group_test",
                "data-group-prefix": "_group_",
            }
        )
        assert "custom-class" in widget.attrs["class"]
        assert "selectpicker-group-aware" in widget.attrs["class"]


def describe_group_key_and_prefix_properties():
    def it_returns_group_key_from_attrs():
        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )
        assert widget.group_key == "_group_publishers"

    def it_returns_group_prefix_from_attrs():
        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_test", "data-group-prefix": "_custom_"}
        )
        assert widget.group_prefix == "_custom_"


def describe_value_from_datadict():
    def it_returns_empty_list_when_no_data():
        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_test", "data-group-prefix": "_group_"}
        )
        result = widget.value_from_datadict({}, {}, "test_field")
        assert result == []

    def it_returns_normal_values_when_no_group_values(publishers):
        penguin = publishers["penguin"]
        harpercollins = publishers["harpercollins"]

        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )
        data = {"publishers": [str(penguin.pk), str(harpercollins.pk)]}
        result = widget.value_from_datadict(data, {}, "publishers")

        assert str(penguin.pk) in result
        assert str(harpercollins.pk) in result
        assert len(result) == 2

    def it_encodes_group_tokens_from_querydict(publishers):
        penguin = publishers["penguin"]

        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )
        data = QueryDict(mutable=True)
        data.setlist("publishers", [str(penguin.pk)])
        data.setlist("_group_publishers", ["New York", "Los Angeles"])

        result = widget.value_from_datadict(data, {}, "publishers")

        assert str(penguin.pk) in result
        assert "_group_publishers:New York" in result
        assert "_group_publishers:Los Angeles" in result
        assert len(result) == 3

    def it_encodes_group_tokens_from_regular_dict(publishers):
        penguin = publishers["penguin"]

        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )
        data = {
            "publishers": [str(penguin.pk)],
            "_group_publishers": "New York,Los Angeles",
        }

        result = widget.value_from_datadict(data, {}, "publishers")

        assert str(penguin.pk) in result
        assert "_group_publishers:New York" in result
        assert "_group_publishers:Los Angeles" in result
        assert len(result) == 3

    def it_handles_empty_group_values(publishers):
        penguin = publishers["penguin"]

        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )
        data = QueryDict(mutable=True)
        data.setlist("publishers", [str(penguin.pk)])
        data.setlist("_group_publishers", [])

        result = widget.value_from_datadict(data, {}, "publishers")

        assert str(penguin.pk) in result
        assert len(result) == 1


def describe_render_method():
    def it_renders_select_element_with_values(publishers):
        penguin = publishers["penguin"]
        harpercollins = publishers["harpercollins"]

        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )

        html = widget.render("publishers", [str(penguin.pk), str(harpercollins.pk)])
        soup = BeautifulSoup(html, features="html.parser")

        select = soup.find("select")
        assert select is not None
        assert "selectpicker-group-aware" in select.get("class", [])

    def it_renders_hidden_inputs_for_group_tokens(publishers):
        penguin = publishers["penguin"]

        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )

        # Render with both normal value and group tokens
        value = [str(penguin.pk), "_group_publishers:New York", "_group_publishers:Los Angeles"]
        html = widget.render("publishers", value)
        soup = BeautifulSoup(html, features="html.parser")

        # Check hidden inputs for group values
        hidden_inputs = soup.find_all("input", attrs={"type": "hidden", "class": "group-injected"})
        assert len(hidden_inputs) == 2

        hidden_values = [inp.get("value") for inp in hidden_inputs]
        assert "Los Angeles" in hidden_values
        assert "New York" in hidden_values

        # All hidden inputs should have the group key as name
        for inp in hidden_inputs:
            assert inp.get("name") == "_group_publishers"

    def it_separates_group_tokens_from_normal_values_in_select(publishers):
        penguin = publishers["penguin"]

        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )

        # Render with both normal value and group token
        value = [str(penguin.pk), "_group_publishers:New York"]
        html = widget.render("publishers", value)
        soup = BeautifulSoup(html, features="html.parser")

        # The select should only show normal values as selected
        # (group tokens should not appear as selected options)
        select = soup.find("select")
        assert select is not None

        # Hidden inputs for group
        hidden_inputs = soup.find_all("input", attrs={"type": "hidden"})
        assert len(hidden_inputs) > 0

    def it_handles_empty_value(publishers):
        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )

        html = widget.render("publishers", [])
        soup = BeautifulSoup(html, features="html.parser")

        select = soup.find("select")
        assert select is not None

        # No hidden inputs when no group tokens
        hidden_inputs = soup.find_all("input", attrs={"type": "hidden", "class": "group-injected"})
        assert len(hidden_inputs) == 0

    def it_handles_none_value(publishers):
        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )

        html = widget.render("publishers", None)
        soup = BeautifulSoup(html, features="html.parser")

        select = soup.find("select")
        assert select is not None

    def it_deduplicates_group_values_in_hidden_inputs(publishers):
        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )

        # Pass duplicate group tokens
        value = [
            "_group_publishers:New York",
            "_group_publishers:New York",
            "_group_publishers:Los Angeles",
        ]
        html = widget.render("publishers", value)
        soup = BeautifulSoup(html, features="html.parser")

        hidden_inputs = soup.find_all("input", attrs={"type": "hidden", "class": "group-injected"})
        # Should be deduplicated
        assert len(hidden_inputs) == 2

    def it_sorts_group_values_in_hidden_inputs(publishers):
        widget = GroupAwareBootstrapMultiSelect(
            attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
        )

        value = [
            "_group_publishers:Zebra",
            "_group_publishers:Apple",
            "_group_publishers:Mango",
        ]
        html = widget.render("publishers", value)
        soup = BeautifulSoup(html, features="html.parser")

        hidden_inputs = soup.find_all("input", attrs={"type": "hidden", "class": "group-injected"})
        hidden_values = [inp.get("value") for inp in hidden_inputs]

        # Should be sorted
        assert hidden_values == ["Apple", "Mango", "Zebra"]


def describe_integration_with_form():
    def it_works_with_model_multiple_choice_field(publishers):
        class TestForm(Form):
            publishers = ModelMultipleChoiceField(
                queryset=Publisher.objects.all(),
                widget=GroupAwareBootstrapMultiSelect(
                    attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
                ),
            )

        form = TestForm()
        soup = BeautifulSoup(form.as_p(), features="html.parser")

        select = soup.find("select", attrs={"name": "publishers"})
        assert select is not None
        assert "selectpicker-group-aware" in select.get("class", [])

    def it_renders_all_publishers_as_options(publishers):
        class TestForm(Form):
            publishers = ModelMultipleChoiceField(
                queryset=Publisher.objects.all(),
                widget=GroupAwareBootstrapMultiSelect(
                    attrs={"data-group-key": "_group_publishers", "data-group-prefix": "_group_"}
                ),
            )

        form = TestForm()
        soup = BeautifulSoup(form.as_p(), features="html.parser")

        options = soup.find_all("option")
        # Should have options for all publishers
        assert len(options) >= 3
