from bs4 import BeautifulSoup
from django import forms
from django.forms.widgets import HiddenInput
from django.template import RequestContext
from dynpy_actions.actions import ModelViewActions
from dynpy_actions.enums import EmbedType
from dynpy_actions.mixins import AutoFillFormFromKwargsMixin


class TestActionWithAutoFill(AutoFillFormFromKwargsMixin, ModelViewActions):
    element = forms.CharField()
    name = "test_action_with_auto_fill"
    embed_type = EmbedType.MODAL
    pre_render = True


def test_auto_fills_fields_with_same_name(rf):
    action = TestActionWithAutoFill()
    form_class = action.get_form_class()
    form_class.base_fields["new_field"] = forms.CharField(widget=HiddenInput())
    action.element = form_class
    request = rf.get("/")
    context = RequestContext(request, {})

    rendered_template = action.render_action(request, context, new_field=100)

    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.form.select_one("#id_new_field").attrs["value"] == "100"


def test_does_not_set_value_of_model_instance(rf, django_user_model):
    """
    Do not want model instance to get overridden by the autofill.
    If it would, it would no longer be the serialized version.
    """
    action = TestActionWithAutoFill()
    form_class = action.get_form_class()
    action.element = form_class
    request = rf.get("/")
    context = RequestContext(request, {})
    model_instance = django_user_model.objects.create()
    rendered_template = action.render_action(request, context, model_instance=model_instance)

    soup = BeautifulSoup(rendered_template, features="html.parser")
    serialized_model_instance = soup.form.select_one("#id_model_instance").attrs["value"]
    expected_serialized_model_instance = f"model_instance___auth___user___{model_instance.pk}"
    assert serialized_model_instance == expected_serialized_model_instance


def test_works_when_there_is_no_model_instance(rf):
    action = TestActionWithAutoFill()
    form_class = action.get_form_class()
    form_class.base_fields["new_field"] = forms.CharField(widget=HiddenInput())
    action.element = form_class
    request = rf.get("/")
    context = RequestContext(request, {})
    rendered_template = action.render_action(request, context, new_field=100)

    soup = BeautifulSoup(rendered_template, features="html.parser")
    assert soup.form.select_one("#id_new_field").attrs["value"] == "100"
