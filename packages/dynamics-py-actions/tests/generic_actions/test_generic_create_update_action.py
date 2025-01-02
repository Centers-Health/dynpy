import pytest
from django.contrib.messages.api import get_messages

from dynpy_actions.generic_actions import GenericCreateUpdateAction


@pytest.fixture()
def test_generic_action(test_form):
    class TestAction(GenericCreateUpdateAction):
        element = test_form
        name = "test_action"

    return TestAction


@pytest.fixture()
def django_user_model(django_user_model):
    django_user_model._meta.verbose_name = "User"
    return django_user_model


def test_action_can_create_new(test_generic_action, rf, django_user_model, add_middleware_to_request):
    request = rf.post("/", {"action_name": "test_action", "username": "test"})
    request = add_middleware_to_request(request)
    action = test_generic_action()
    form = action.get_initialized_form(request, data=request.POST)
    action.handle(request, form)
    assert django_user_model.objects.count() == 1


def test_action_can_update(
    test_user, test_generic_action, rf, django_user_model, add_middleware_to_request
):
    request = rf.post(
        "/",
        {
            "action_name": "test_action",
            "username": "new_username",
            "model_instance_id": test_user.id,
        },
    )
    request = add_middleware_to_request(request)
    action = test_generic_action()
    form = action.get_initialized_form(request, data=request.POST, model_instance=test_user)
    action.handle(
        request,
        form,
    )
    assert django_user_model.objects.count() == 1
    assert django_user_model.objects.first().username == "new_username"


def test_default_success_message_when_creating_new(
    test_generic_action, rf, django_user_model, add_middleware_to_request
):
    request = rf.post("/", {"action_name": "test_action", "username": "test"})
    request = add_middleware_to_request(request)
    action = test_generic_action()
    form = action.get_initialized_form(request, data=request.POST)
    action.handle(request, form)
    message = get_messages(request)._queued_messages[0].message
    assert message == "User Created Successfully"


def test_default_success_message_when_updating(
    test_user, test_generic_action, rf, django_user_model, add_middleware_to_request
):
    request = rf.post(
        "/",
        {
            "action_name": "test_action",
            "username": "test",
            "model_instance_id": test_user.id,
        },
    )
    request = add_middleware_to_request(request)
    action = test_generic_action()
    form = action.get_initialized_form(request, data=request.POST, model_instance=test_user)
    action.handle(request, form, model_instance=test_user)
    message = get_messages(request)._queued_messages[0].message
    assert message == "User Updated Successfully"


def test_default_error_message_(test_generic_action, rf, django_user_model, add_middleware_to_request):
    request = rf.post("/", {"action_name": "test_action"})
    request = add_middleware_to_request(request)
    action = test_generic_action()
    form = action.get_initialized_form(request, data=request.POST)
    action.handle(request, form)
    message = get_messages(request)._queued_messages[0].message
    assert "User not saved" in message
    assert "Username:</b> This field is required" in message
