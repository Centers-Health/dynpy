import json

import pytest
from bs4 import BeautifulSoup

from dynpy_actions.exceptions import AsyncConfirmNotDefinedException


def test_GET_without_parameters_renders_out_the_parent_template(rf, test_view_with_actions):
    request = rf.get(
        "/",
    )
    response = test_view_with_actions.as_view()(request)
    assert response.template_name[0] == "dynpy_actions/action_generic_base_form.html"


def test_GET_with_parameters_renders_out_the_form_html(rf, test_user, test_view_with_actions):
    """
    When getting the form the html should have the form but
    not the modal.
    """
    action = test_view_with_actions.actions[0]
    request = rf.get(
        "/",
        {
            "action_action__name": action.name,
            "model_instance_pk": test_user.id,
            "model": test_user._meta.model_name,
            "app_label": test_user._meta.app_label,
        },
    )
    response = test_view_with_actions.as_view()(request)
    soup = BeautifulSoup(response.render().content, features="html.parser")

    assert soup.find("form")
    assert not soup.select(f'button[data-target="#{action.name}Modal{test_user.id}"]')
    assert not soup.select(f"div#{action.name}Modal{test_user.id}")
    assert soup.select('input[name="action_name"]')[0].attrs["value"] == action.name
    assert soup.select('input[name="csrfmiddlewaretoken"]')
    assert soup.select('input[name="username"]')


def test_post_with_action_calls_actions_handle_method(rf, test_view_with_actions):

    action = test_view_with_actions.actions[0]
    request = rf.post(
        "/",
        {
            "action_name": action.name,
        },
    )
    response = test_view_with_actions.as_view()(request)
    assert response.content == b"action handle called"


def test_post_without_action_calls_parent_post(rf, test_view_with_actions):

    request = rf.post(
        "/",
        {
            "arg": {"action_kwargs": "arg"},
        },
    )
    test_view_with_actions.template_name = "tests/dummy_template.html"
    response = test_view_with_actions.as_view()(request)
    assert response.template_name[0] == "tests/dummy_template.html"
    assert response._request.method == "POST"
    assert response.render().content != b"action handle called"


def describe_async_confirm():
    def when_true_calls_async_confirm(rf, test_view_with_actions):
        # Arrange
        action = test_view_with_actions.actions[0]
        action.async_confirmation = True
        action.async_validation = False
        action.async_confirm = lambda self, request, form: "Are you sure"

        # Act
        request = rf.post(
            "/",
            {"action_name": action.name, "confirm": "true"},
        )

        response = test_view_with_actions.as_view()(request)
        confirm_message = json.loads(response.content).get("message")

        # Assert
        assert confirm_message == "Are you sure"

    def it_errors_when_async_confirm_not_defined(rf, test_view_with_actions):
        # Arrange
        action = test_view_with_actions.actions[0]
        action.async_confirmation = True
        action.async_validation = False

        # Act
        request = rf.post(
            "/",
            {"action_name": action.name, "confirm": "true"},
        )
        with pytest.raises(AsyncConfirmNotDefinedException):
            test_view_with_actions.as_view()(request)

    def it_does_not_check_async_confirm_if_the_form_is_invalid(rf, test_view_with_actions):
        # Arrange
        action = test_view_with_actions.actions[0]
        action.async_confirmation = True
        action.async_validation = True

        # Act
        request = rf.post(
            "/",
            {
                "action_name": action.name,
                "confirm": "true",
                "validate": True,
                "username": "!@#",
            },
        )
        response = test_view_with_actions.as_view()(request)
        message = json.loads(response.content).get("message")
        assert message is None


def describe_async_validate():
    def when_true_calls_async_validate(rf, test_view_with_actions):
        # Arrange
        action = test_view_with_actions.actions[0]
        action.async_confirmation = False
        action.async_validation = True
        action.async_confirm = lambda self, request, form: "Are you sure"

        # Act
        request = rf.post(
            "/",
            {"action_name": action.name, "validate": "true", "username": "!@$"},
        )

        response = test_view_with_actions.as_view()(request)
        errors = json.loads(response.content).get("errors")

        # Assert
        assert (
            errors["username"][0]["message"]
            == "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."
        )
