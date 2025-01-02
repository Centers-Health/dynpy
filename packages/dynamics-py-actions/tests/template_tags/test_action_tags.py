import pytest
from bs4 import BeautifulSoup
from django.template import RequestContext

from dynpy_actions import constants
from dynpy_actions.enums import EmbedType
from dynpy_actions.exceptions import ActionNotFoundException
from dynpy_actions.templatetags.actions_tags import (
    build_url_with_query,
    render_action_template,
    render_button_attributes,
    render_kwargs_as_data_attributes,
)


def test_template_tag_render_action_template_renders_the_action_template(rf, test_user, test_action):
    test_action = test_action()
    request = rf.get("")
    context = RequestContext(request, {})
    context["request"] = request
    context["actions"] = {test_action.name: test_action}

    rendered_template = render_action_template(
        context,
        test_action,
        test=test_user,
    )
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.find("form")
    assert soup.select('input[name="action_name"]')[0].attrs["value"] == "test_action"
    assert soup.select('input[name="csrfmiddlewaretoken"]')
    assert soup.select('input[name="username"]')


def test_render_action_template_works_without_model_instance(test_user, test_action, rf):
    """
    When using an action to create new, there won't be a model instance.
    """
    test_action = test_action()
    request = rf.get("")
    context = RequestContext(request, {})
    context["request"] = request
    context["actions"] = {test_action.name: test_action}

    rendered_template = render_action_template(context, test_action)

    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.find("form")
    assert soup.select('input[name="action_name"]')[0].attrs["value"] == test_action.name
    assert soup.select('input[name="username"]')


def test_render_kwargs_as_data_attributes():
    data_attributes = render_kwargs_as_data_attributes({"kwarg1": "kwarg1", "kwarg2": "kwarg2"})
    assert 'data-action_kwarg1 = "kwarg1"  data-action_kwarg2 = "kwarg2" ' in data_attributes


def test_render_button_attributes(test_action):
    action = test_action()
    action.button_attributes = {"id": "123", "class": "btn", "disabled": True}
    attributes = render_button_attributes(action)
    assert attributes == ' id="123" class="btn" disabled'


@pytest.mark.parametrize("embed_type", [EmbedType.MODAL])
def test_render_button_attributes_defaults(test_action, embed_type):
    action = test_action()
    action.embed_type = embed_type
    action.pre_render = False
    action.button_attributes = {}
    attributes = render_button_attributes(action)

    assert attributes == ' class="btn btn-primary btn-sm " data-js-load-action-form'


def test_raises_ActionNotFoundException_if_action_not_found(test_action, rf):
    test_action = test_action()
    request = rf.get("")
    context = RequestContext(request, {})
    context["request"] = request
    context["actions"] = {}
    with pytest.raises(ActionNotFoundException):
        render_action_template(
            context,
            "fake action",
        )


def describe_dict_to_params():
    def it_builds_url_string_from_dict():
        url = "/"
        url_with_params = build_url_with_query(url, {"key": "value"})
        assert url_with_params == f"/?{constants.ACTION_KWARGS_PREFIX}key=value"

    def it_adds_in_question_mark_if_not_there():
        url = "/"
        url_with_params = build_url_with_query(url, {"key": "value"})
        assert "?" in url_with_params

    def it_does_not_add_in_question_mark_if_already_there():
        url = "/?key=value"
        url_with_params = build_url_with_query(url, {"key": "value"})
        assert url_with_params.count("?") == 1
