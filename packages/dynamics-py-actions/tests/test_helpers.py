import pytest
from django.template import RequestContext
from dynpy_actions.exceptions import ActionNotFoundException
from dynpy_actions.helpers import deserialize_kwargs, serialize_kwargs
from dynpy_actions.templatetags.actions_tags import render_action_template


def test_serialize_kwargs_returns_an_object_as_string_of_app_label_model_and_id(
    test_user,
):
    serialized_kwargs = serialize_kwargs(user=test_user)
    assert serialized_kwargs["user"] == f"model_instance___auth___user___{test_user.id}"


def test_deserialize_kwargs_returns_a_serialized_object_as_the_original_object(
    test_user,
):
    deserialized_kwargs = deserialize_kwargs(user=f"model_instance___auth___user___{test_user.id}")
    assert deserialized_kwargs["user"] == test_user


@pytest.mark.parametrize(
    ("serialized_value", "deserialized_value"),
    [("True", True), ("False", False)],
)
def test_deserialize_kwargs_returns_a_bool_when_given_a_string(serialized_value, deserialized_value):
    deserialized_kwargs = deserialize_kwargs(test_bool=serialized_value)
    assert deserialized_kwargs["test_bool"] == deserialized_value


def test_deserialize_kwargs_only_replaces_action_once():
    deserialized_kwargs = deserialize_kwargs(action_action_name="test")
    assert deserialized_kwargs["action_name"]


def test_validate_action_prints_a_list_of_the_actions_in_the_view(test_model_action, rf):
    request = rf.get("")
    context = RequestContext(request, {})
    context["request"] = request
    context["actions"] = {test_model_action.name: test_model_action}

    with pytest.raises(ActionNotFoundException) as e:
        render_action_template(
            context,
            "fake action",
        )
    assert test_model_action.name in str(e)
