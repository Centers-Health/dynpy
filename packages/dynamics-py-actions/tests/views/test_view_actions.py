import hashlib

import pytest
from bs4 import BeautifulSoup
from django import forms
from django.forms.fields import ChoiceField
from django.http.request import HttpRequest
from django.template import RequestContext
from django.views.generic import View

from dynpy_actions.actions import ViewActions
from dynpy_actions.enums import EmbedType
from dynpy_actions.exceptions import ConflictingConfirmationsException, TargetNotSpecifiedException
from dynpy_actions.mixins import AutoFillFormFromKwargsMixin, ViewActionsMixin
from dynpy_actions.utils.testing_utils import handle_action


def test_id_is_reset_after_100000_actions_are_rendered(test_action):
    """
    Id should reset after the counter reaches 100,000.
    Test is asserting that it resets after it reaches
    100,000 (the action has id less than 100,000).
    """
    action_list = []
    for _ in range(100_001):
        action_list.append(test_action())
    assert action_list[-1]._id < 100_000


def test_render_template_works(rf, test_user, test_action):
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action().render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.find("form")
    assert soup.select('input[name="action_name"]')[0].attrs["value"] == "test_action"
    assert soup.select('input[name="csrfmiddlewaretoken"]')
    assert soup.select('input[name="username"]')


def test_can_render_action_with_form_field_as_element(rf, test_user, test_action):

    test_action.element = ChoiceField(choices=[(1, "a")])

    request = rf.get("")
    context = RequestContext(request, {})
    rendered_template = test_action().render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.find("form")
    assert soup.select('input[name="action_name"]')[0].attrs["value"] == "test_action"
    assert soup.select('input[name="csrfmiddlewaretoken"]')
    assert soup.select('option[value="1"]')


def test_render_action_template_renders_an_inline_element(rf, test_user, test_action):
    test_action = test_action()
    test_action.embed_type = EmbedType.INLINE
    request = rf.get("/")
    context = RequestContext(request, {})
    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.find("form")
    assert "form-inline" in soup.find("form").attrs.get("class")
    assert soup.select('input[name="action_name"]')[0].attrs["value"] == "test_action"
    assert soup.select('input[name="csrfmiddlewaretoken"]')
    assert soup.select('input[name="username"]')


def test_action_correctly_renders_a_modal_element(rf, test_user, test_action):
    test_action = test_action()

    test_action.embed_type = EmbedType.MODAL
    test_action.button_value = "Click Me"
    request = rf.get("/")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")

    assert soup.find("form")
    assert soup.select(f'button[data-target="#{test_action.name}_{test_action._id}"]')
    assert soup.select(f"div#{test_action.name}_{test_action._id}")
    assert soup.select('input[name="action_name"]')[0].attrs["value"] == test_action.name
    assert soup.select('input[name="csrfmiddlewaretoken"]')
    assert soup.select('input[name="username"]')
    assert soup.button.text.strip() == "Click Me"


def test_action_correctly_renders_a_target_action(rf, test_user, test_action):
    test_action = test_action()

    test_action.embed_type = EmbedType.TARGET
    test_action.target_elem_id = "target"
    test_action.pre_render = False
    request = rf.get("/")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    assert "data-js-load-action-form" in rendered_template
    assert 'data-action-type="target"' in rendered_template


def test_target_action_raises_exception_if_no_target_set(rf, test_user, test_action):
    test_action = test_action()

    test_action.embed_type = EmbedType.TARGET
    request = rf.get("/")
    context = RequestContext(request, {})
    with pytest.raises(TargetNotSpecifiedException):
        test_action.render_action(request, context, model_instance=test_user)


@pytest.mark.parametrize("embed_type", [(EmbedType.INLINE), (EmbedType.MODAL)])
def test_non_pre_rendered_action_does_not_have_form(rf, test_user, test_action, embed_type):
    test_action = test_action()

    test_action.pre_render = False
    test_action.embed_type = embed_type
    request = rf.get("")
    context = RequestContext(request, {})
    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert not soup.find("form")


@pytest.mark.parametrize("embed_type", [(EmbedType.INLINE), (EmbedType.MODAL)])
def test_pre_rendered_action_has_form(rf, test_user, test_action, embed_type):
    test_action = test_action()
    test_action.embed_type = embed_type

    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.find("form")
    assert soup.select('input[name="action_name"]')[0].attrs["value"] == "test_action"
    assert soup.select('input[name="username"]')


def test_action_renders_class_if_needs_confirmation(rf, test_action, test_user):
    test_action = test_action()
    test_action.needs_confirmation = True
    test_action.confirmation_text = "abcd"
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")

    assert "js-form-confirm" in soup.find("form").attrs.get("class")
    assert "abcd" in soup.find("form").attrs.get("data-message")


def test_that_handle_method_is_required(rf, test_view_with_actions):
    action = test_view_with_actions.actions[0]
    action.handle = ViewActions.handle  # Reset handle function to the base handle
    request = rf.post("/", {"action_name": action.name})
    with pytest.raises(NotImplementedError):
        test_view_with_actions.as_view()(request)


def test_all_kwargs_passed_into_action_are_set_as_data_attributes_in_template(rf, test_action):
    action = test_action()

    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = action.render_action(request, context, kwarg_1="kwarg_1", kwarg_2="kwarg_2")
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert "data-action_kwarg_1" in soup.select_one('div[id^="actions_wrapper"]').attrs
    assert "data-action_kwarg_2" in soup.select_one('div[id^="actions_wrapper"]').attrs


def test_action_redirects_to_current_page_if_get_success_url_is_not_defined(
    test_form,
    test_user,
    rf,
    add_middleware_to_request,
):
    class ActionWithoutSuccessURL(ViewActions):
        element = test_form
        name = "test_action"

        def handle(self, request, form, **kwargs):
            pass

    class TestView(ViewActionsMixin, View):
        actions = [ActionWithoutSuccessURL]
        template_name = "dynpy_actions/action_generic_base_form.html"

    request = rf.post(
        "/",
        {"action_name": "test_action", "model_instance_id": test_user.id},
    )
    request.META["HTTP_REFERER"] = "https://ar.localhost"

    request = add_middleware_to_request(request)
    response = TestView.as_view()(request)

    assert response.status_code == 302
    assert response.url == "https://ar.localhost"


def test_action_redirects_to_success_url_if_get_success_url_is_defined(
    test_form,
    test_user,
    rf,
    add_middleware_to_request,
):
    class ActionWithGetSuccessURL(ViewActions):
        element = test_form
        name = "test_action"

        def handle(self, request, form, **kwargs):
            pass

        def get_success_url(self, request: HttpRequest):
            return "dummy_path"

    class TestView(ViewActionsMixin, View):
        actions = [ActionWithGetSuccessURL]
        template_name = "dynpy_actions/action_generic_base_form.html"

    request = rf.post(
        "/",
        {"action_name": "test_action", "model_instance_id": test_user.id},
    )
    request = add_middleware_to_request(request)
    response = TestView.as_view()(request)

    assert response.status_code == 302
    assert response.url == "dummy_path"


def test_action_redirects_to_success_url_if_success_url_is_defined(
    test_form,
    test_user,
    rf,
    add_middleware_to_request,
):
    class ActionWithSuccessURL(ViewActions):
        element = test_form
        name = "test_action"
        success_url = "dummy_path"

        def handle(self, request, form, **kwargs):
            pass

    class TestView(ViewActionsMixin, View):
        actions = [ActionWithSuccessURL]
        template_name = "dynpy_actions/action_generic_base_form.html"

    request = rf.post(
        "/",
        {"action_name": "test_action", "model_instance_id": test_user.id},
    )
    request = add_middleware_to_request(request)
    response = TestView.as_view()(request)

    assert response.status_code == 302
    assert response.url == "dummy_path"


# ---------------------------------------------------------------------------- #
#                               Autosubmit Tests                               #
# ---------------------------------------------------------------------------- #
def test_action_does_not_render_submit_button_if_autosubmit_is_true(rf, test_action, test_user):
    test_action = test_action()
    test_action.autosubmit = True
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")

    assert not soup.select('input[type="submit"]')


def test_action_renders_submit_button_by_default(rf, test_action, test_user):
    test_action = test_action()
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")

    assert soup.select('input[type="submit"]')


def test_action_renders_class_if_autosubmit_is_true(rf, test_action, test_user):
    test_action = test_action()
    test_action.autosubmit = True
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")

    assert "js-form-autosubmit" in soup.find("form").attrs.get("class")


def test_action_does_not_render_autosubmit_javascript_by_default(rf, test_action, test_user):
    test_action = test_action()
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")

    assert "onchange" not in soup.find("form").attrs


# ---------------------------------------------------------------------------- #
#                     Testing Dynamic Attributes                               #
# ---------------------------------------------------------------------------- #
def test_can_override_get_form_kwargs_to_dynamically_add_to_the_form(test_action, rf, test_user):

    test_action = test_action()
    request = rf.get("")
    context = RequestContext(request, {})

    def get_form_kwargs_test(request, FormClass, **kwargs):
        form_kwargs = {"initial": {}}
        form_kwargs["initial"]["username"] = "abcd"
        return form_kwargs

    test_action.get_form_kwargs = get_form_kwargs_test

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.form.select_one('div[id="div_id_username"]').input.attrs["value"] == "abcd"


def test_can_override_get_button_attributes_to_dynamically_change_it(rf, test_form):
    request = rf.get("")
    context = RequestContext(request, {})

    class TestAction(ViewActions):

        element = test_form
        embed_type = EmbedType.MODAL
        pre_render = True
        name = "action_with_button_attributes"

        def get_button_attributes(self, request, **kwargs):
            attrs = self.button_attributes
            attrs["test"] = 123
            return attrs

    test_action = TestAction()
    rendered_template = test_action.render_action(request, context)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.button.attrs["test"] == "123"


def test_can_override_get_addional_button_classes_to_dynamically_change_it(rf, test_form):
    request = rf.get("")
    context = RequestContext(request, {})

    class TestAction(ViewActions):

        element = test_form
        embed_type = EmbedType.MODAL
        pre_render = True
        name = "action_with_additional_button_classes"

        def get_additional_button_classes(self, request, **kwargs):
            classes = self.additional_button_classes
            classes.append("test_class")
            return classes

    test_action = TestAction()
    rendered_template = test_action.render_action(request, context)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert "test_class" in soup.button.attrs["class"]


def test_can_override_get_confirmation_text_to_dynamically_change_it(test_action, rf, test_user):

    test_action = test_action()
    test_action.needs_confirmation = True

    def get_confirmation_text(request, **kwargs):
        return "abcd"

    test_action.get_confirmation_text = get_confirmation_text
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert "abcd" in soup.find("form").attrs.get("data-message")


def test_can_override_get_needs_confirmation_to_dynamically_change_it(test_action, rf, test_user):

    test_action = test_action()
    test_action.confirmation_text = "abcd"

    def get_needs_confirmation(request, **kwargs):
        return True

    test_action.get_needs_confirmation = get_needs_confirmation
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert "js-form-confirm" in soup.find("form").attrs.get("class")


def test_can_override_get_modal_button_value_to_dynamically_change_it(test_action, rf, test_user):

    test_action = test_action()
    test_action.embed_type = EmbedType.MODAL

    def get_modal_button_value(request, **kwargs):
        return "abcd"

    test_action.get_modal_button_value = get_modal_button_value
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.button.text.strip() == "abcd"


def test_can_override_get_validate_on_to_dynamically_change_it(test_action, rf, test_user):

    test_action = test_action()
    test_action.validate_on = "submit"

    def get_validate_on(request, **kwargs):
        return "change"

    test_action.get_validate_on = get_validate_on
    request = rf.get("")
    context = RequestContext(request, {})

    rendered_template = test_action.render_action(request, context, model_instance=test_user)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.form.attrs.get("data-validate-on") == "change"


def test_using_modal_button_value_property_raises_warning(rf, test_action, test_user):
    action = test_action()
    test_action.embed_type = EmbedType.MODAL
    action.modal_button_value = "Click Me"
    request = rf.get("")
    context = RequestContext(request, {})
    with pytest.warns(
        PendingDeprecationWarning,
        match="modal_button_value is deprecated use button_value instead",
    ):
        action.render_action(request, context, model_instance=test_user)


def test_overriding_get_modal_button_value_raises_warning(rf, test_action, test_user):
    action = test_action()

    def get_modal_button_value(request: HttpRequest, **kwargs) -> str:
        return "Click Me"

    action.get_modal_button_value = get_modal_button_value
    request = rf.get("")
    context = RequestContext(request, {})
    with pytest.warns(
        PendingDeprecationWarning,
        match=r"get_modal_button_value\(\) is deprecated use get_button_value\(\) instead",
    ):
        action.render_action(request, context, model_instance=test_user)


def test_overriding_get_popover_button_value_raises_warning(rf, test_action, test_user):
    action = test_action()

    def get_popover_button_value(request: HttpRequest, **kwargs) -> str:
        return "Click Me"

    action.get_popover_button_value = get_popover_button_value
    request = rf.get("")
    context = RequestContext(request, {})
    with pytest.warns(
        PendingDeprecationWarning,
        match=r"get_popover_button_value\(\) is deprecated use get_button_value\(\) instead",
    ):
        action.render_action(request, context, model_instance=test_user)


def test_button_attributes_are_set_as_html_attributes_on_the_button_in_template(rf, test_form):
    class ActionWithButtonAttributes(ViewActions):

        element = test_form
        embed_type = EmbedType.MODAL
        pre_render = True
        name = "action_with_button_attributes"
        button_attributes = {"id": "123", "class": "myclass", "disabled": True}

        def handle(self, request, form, **kwargs):
            pass

    action = ActionWithButtonAttributes()
    request = rf.get("")
    context = RequestContext(request, {})
    rendered_template = action.render_action(request, context)
    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.button.get("id") == "123"
    assert soup.button.get("class") == ["myclass"]
    assert "disabled" in soup.button.attrs


def test_additional_button_classes_are_set_as_css_classes_on_the_button_in_template(rf, test_form):
    class ActionWithAdditionalButtonClasses(ViewActions):

        element = test_form
        embed_type = EmbedType.MODAL
        pre_render = True
        name = "action_with_additional_button_classes"
        additional_button_classes = ["myclass-1", "myclass-2"]

        def handle(self, request, form, **kwargs):
            pass

    action = ActionWithAdditionalButtonClasses()
    request = rf.get("")
    context = RequestContext(request, {})
    rendered_template = action.render_action(request, context)
    soup = BeautifulSoup(rendered_template, features="html.parser")

    classes = soup.button.get("class")

    # assert it has additional classes and it does not override defaults
    assert all(c in classes for c in ["myclass-1", "myclass-2", "btn", "btn-primary", "btn-sm"])


def test_hash_only_uses_action_name_by_default(test_action, rf):
    action = test_action()
    request = rf.get("")
    actions_hash = action.get_hash(request)

    hashable_string = action.name
    hasher = hashlib.sha256()
    string_as_bytes = str.encode(hashable_string)

    hasher.update(string_as_bytes)
    hash = hasher.hexdigest()
    assert hash == actions_hash


def test_model_instance_is_added_by_default_hashing_list(test_action, rf):
    action = test_action()
    request = rf.get("")
    action.get_hashing_list = lambda request, **kwargs: [1]
    actions_hash = action.get_hash(request)

    hashable_string = action.name + "1"
    hasher = hashlib.sha256()
    string_as_bytes = str.encode(hashable_string)

    hasher.update(string_as_bytes)
    hash = hasher.hexdigest()
    assert hash == actions_hash


def describe_form_template_attribute():
    def when_defined_its_used_by_render_form(test_action, rf):
        action = test_action()
        request = rf.get("/")
        view_context = RequestContext(request)

        action.form_template = "tests/dummy_template.html"
        content = action.render_form(request, view_context).render().content
        assert b"I am a dummy template" in content

    def when_defined_its_used_by_render_action(test_action, rf):
        action = test_action()
        request = rf.get("/")
        view_context = RequestContext(request)

        action.form_template = "tests/dummy_template.html"
        content = action.render_action(request, view_context)
        assert "I am a dummy template" in content


def test_conflicting_confirmations_raises_an_exception(test_action, rf):
    test_action.async_confirmation = True
    test_action.needs_confirmation = True
    request = rf.get("/")

    with pytest.raises(ConflictingConfirmationsException):
        test_action()._set_all_attributes(request)


def describe_force_initial_fields():
    class TestActionWithAutoFill(AutoFillFormFromKwargsMixin, ViewActions):
        element = forms.CharField()
        name = "test_action_with_auto_fill"
        embed_type = EmbedType.MODAL
        pre_render = True
        force_initial_fields = ["new_field"]

        def get_form_class(self):
            form_class = super().get_form_class()
            form_class.base_fields["new_field"] = forms.CharField(widget=forms.HiddenInput())
            return form_class

        def handle(self, request, form, **kwargs):
            return form.data

    def it_forces_initial_values_that_are_supposed_to_be_forced():
        action = TestActionWithAutoFill()
        action.force_initial_fields = ["new_field"]
        data = handle_action(action, action_kwargs={"new_field": "100"}, input={"new_field": "200"})
        assert data["new_field"] == "100"

    def all_forces_all_kwargs_values():
        action = TestActionWithAutoFill()
        action.force_initial_fields = "__all__"
        data = handle_action(action, action_kwargs={"new_field": "100"}, input={"new_field": "200"})
        assert data["new_field"] == "100"

    def it_does_not_force_initial_fields_that_are_not_supposed_to_be_forced():
        action = TestActionWithAutoFill()
        action.force_initial_fields = []
        data = handle_action(action, action_kwargs={"new_field": "100"}, input={"new_field": "200"})
        assert data["new_field"] == "200"
