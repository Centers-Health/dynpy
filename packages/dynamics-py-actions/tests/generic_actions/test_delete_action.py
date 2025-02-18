import pytest
from django.contrib.messages.api import get_messages

from dynpy_actions.generic_actions import DeleteAction
from dynpy_actions.helpers import serialize_kwargs
from dynpy_actions.utils.testing_utils import handle_action

pytestmark = pytest.mark.django_db()


def test_it_deletes_model_instance(rf, add_middleware_to_request, test_user, django_user_model):
    request = rf.post(
        "/",
        serialize_kwargs(
            action_name="delete",
            model_instance=test_user,
        ),
    )

    request = add_middleware_to_request(request)
    handle_action(
        DeleteAction(),
        action_kwargs={"model_instance": test_user},
    )

    assert django_user_model.objects.exists() is False


def test_default_success_message(rf, add_middleware_to_request, test_user, django_user_model):
    request = rf.post(
        "/",
    )

    request = add_middleware_to_request(request)
    DeleteAction().handle(request, None, model_instance=test_user)
    message = get_messages(request)._queued_messages[0].message

    assert message == "User Deleted Successfully"


def test_get_model_name_returns_model_name(rf, add_middleware_to_request):
    request = rf.post(
        "/",
        {
            "action_name": "delete",
            "model_instance": "model_instance___auth___user___100",
        },
    )

    request = add_middleware_to_request(request)
    action = DeleteAction()
    model_name = "supermodel"
    action.model_name = model_name
    value = action.get_model_name(request, **request.POST)
    assert value == model_name


@pytest.mark.parametrize(
    "model_name",
    ["", None],
)
def test_get_model_name_meta_verbose_name_if_falsey_model_name(
    test_user, rf, add_middleware_to_request, model_name
):
    verbose_name = "Verbose"
    test_user._meta.verbose_name = verbose_name
    request = rf.post(
        "/",
        {},
    )

    request = add_middleware_to_request(request)
    action = DeleteAction()
    action.model_name = model_name
    value = action.get_model_name(request, action_name="delete", model_instance=test_user)

    assert verbose_name == value


def test_no_model_name_field_still_works_and_returns_meta_verbose_name(
    test_user, rf, add_middleware_to_request
):
    verbose_name = "Verbose"
    test_user._meta.verbose_name = verbose_name
    request = rf.post(
        "/",
        {},
    )

    request = add_middleware_to_request(request)
    action = DeleteAction()
    with pytest.raises(AttributeError):
        action.model_name
    value = action.get_model_name(request, action_name="delete", model_instance=test_user)
    assert verbose_name == value
