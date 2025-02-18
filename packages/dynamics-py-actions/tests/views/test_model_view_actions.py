import pytest
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.template import RequestContext
from dynpy_actions.helpers import serialize_kwargs


@pytest.mark.django_db
def test_that_model_forms_have_instance_set_to_the_model_instance(rf, test_view_with_actions, test_user):
    request = rf.get("")
    response = test_view_with_actions.as_view()(request)
    expected_user = response.context_data["view"].actions[1]().get_form(test_user).instance
    assert test_user == expected_user


@pytest.mark.django_db
def test_action_raises_exception_if_does_not_have_model_instance_id_and_allow_create_new_is_false(
    test_view_with_actions, rf, test_model_action
):
    """
    If there is no model_instance and allow_create_new is False an
    exception should be raised. A null model_instance_id is only allowed
    if allow_create_new is set to True.
    """
    action = test_model_action
    action.allow_create_new = False

    def save_form(self, request, form, **kwargs):
        data = request.POST
        form = self.get_form(data=data)
        form.save()

    action.handle = save_form
    test_view_with_actions.actions[1] = action
    request = rf.post("/", {"action_name": action.name, "username": "df"})
    with pytest.raises(
        ValueError,
        match="The User could not be created because the data didn't validate",
    ):
        test_view_with_actions.as_view()(request)

    assert User.objects.count() == 0


@pytest.mark.django_db
def test_action_with_allow_create_new_as_true_can_be_used_also_as_an_update_action(
    test_view_with_actions, rf, test_user
):
    """
    An action that has allow_create_new set to True should
    still be able to be used as an update action also,
    therefore if an model_instance_id is passed in then it should
    update instead of creating new.
    """
    action = test_view_with_actions.actions[1]
    action.allow_create_new = True

    def save_form(self, request, form, **kwargs):
        data = request.POST
        form = self.get_form(None, data=data)
        if data["model_instance_id"]:
            form = self.get_form(User.objects.get(id=data["model_instance_id"]), data)
        form.save()

    action.handle = save_form

    request = rf.post(
        "/",
        {
            "action_name": action.name,
            "username": "df",
            "model_instance_id": test_user.id,
        },
    )
    test_view_with_actions.as_view()(request)
    assert User.objects.count() == 1


def test_model_instance_id_field_is_added_to_form(test_model_action, rf, test_user):
    action = test_model_action()
    assert action.get_form_class().base_fields["model_instance_id"]


def test_model_instance_field_is_added_to_form(test_model_action, rf, test_user):
    action = test_model_action()
    assert action.get_form_class().base_fields["model_instance"]


def test_model_instance_id_is_set_in_get_form_kwargs(test_model_action, rf, test_user):
    action = test_model_action()
    request = rf.get("")
    context = RequestContext(request, {})
    rendered_template = action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.form.select_one("input[id='id_model_instance_id']").attrs["value"] == str(test_user.id)


def test_model_instance_is_set_in_get_form_kwargs(test_model_action, rf, test_user):
    action = test_model_action()
    request = rf.get("")
    context = RequestContext(request, {})
    rendered_template = action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    serialized_model_instance = serialize_kwargs(
        model_instance=test_user,
    )["model_instance"]
    model_instance_input_value = soup.form.select_one("input[id='id_model_instance']").attrs["value"]
    assert model_instance_input_value == serialized_model_instance


def test_model_instance_id_is_not_set_in_get_form_kwargs_if_no_model_instance(
    test_model_action, rf, test_user
):
    action = test_model_action()
    action.allow_create_new = True
    request = rf.get("")
    context = RequestContext(request, {})
    rendered_template = action.render_action(request, context)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert not soup.form.select_one("input[id='id_model_instance_id']").attrs.get("value", None)


def test_model_instance_is_not_set_in_get_form_kwargs_if_no_model_instance(
    test_model_action, rf, test_user
):
    action = test_model_action()
    action.allow_create_new = True
    request = rf.get("")
    context = RequestContext(request, {})
    rendered_template = action.render_action(request, context)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert not soup.form.select_one("input[id='id_model_instance']").attrs.get("value", None)


def test_initial_values_are_set_in_get_form_kwargs(test_model_action, rf, test_user):
    action = test_model_action()
    request = rf.get("")
    context = RequestContext(request, {})
    rendered_template = action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.form.select_one("input[id='id_username']").attrs["value"] == str(test_user.username)
    assert soup.form.select_one("input[id='id_first_name']").attrs["value"] == str(test_user.first_name)
    assert soup.form.select_one("input[id='id_last_name']").attrs["value"] == str(test_user.last_name)
