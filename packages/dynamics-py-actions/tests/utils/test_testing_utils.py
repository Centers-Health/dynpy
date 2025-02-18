import re

import pytest
from bs4 import BeautifulSoup
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context, Template

from dynpy_actions.actions import ViewActions
from dynpy_actions.enums import EmbedType, ModalSize
from dynpy_actions.mixins import AutoFillFormFromKwargsMixin
from dynpy_actions.utils.testing_utils import display_action, handle_action


# Helpers
def clean_form_html(html):
    # remove newline characters and spaces
    re.sub(r"[\\n\s]", "", html)

    # replace csrf token
    re.sub(r'csrfmiddlewaretoken"\s?value="[A-Za-z0-9]+"', 'csrfmiddlewaretoken" value=""', html)


class TestForm(forms.Form):
    name = forms.CharField(required=False)
    is_true = forms.BooleanField()
    the_date = forms.DateField()


def describe_display_action_helper():
    @pytest.mark.parametrize(
        "action_embed_type", [EmbedType.MODAL, EmbedType.INLINE, EmbedType.TARGET, EmbedType.BASE]
    )
    def it_returns_the_action_html(action_embed_type, rf):
        class TestAction(ViewActions):
            name = "test_action"
            embed_type = action_embed_type
            element = TestForm
            pre_render = True

            # for target
            target_elem_id = "test-id"

            # for modal
            modal_size = ModalSize.LARGE

        test_action = TestAction()

        template = Template(
            """
            {% load actions_tags %}
            {% render_action_template actions.test_action %}
            """
        )
        request = rf.get("/")
        context = Context({"request": request, "actions": {"test_action": test_action}})
        rendered_action = template.render(context)
        rendered_action_by_helper = display_action(test_action)

        assert clean_form_html(rendered_action_by_helper) == clean_form_html(rendered_action)

    def it_handles_action_arguments_correctly(rf):
        class TestAction(AutoFillFormFromKwargsMixin, ViewActions):
            name = "test_action"
            embed_type = EmbedType.MODAL
            element = TestForm
            pre_render = True

        test_action = TestAction()

        template = Template(
            """
            {% load actions_tags %}
            {% render_action_template actions.test_action name=name %}
            """
        )
        request = rf.get("/")
        context = Context({"request": request, "name": "john", "actions": {"test_action": test_action}})
        rendered_action = template.render(context)
        rendered_action_by_helper = display_action(test_action, action_kwargs={"name": "john"})

        rendered_action_soup = BeautifulSoup(rendered_action, features="html.parser")
        rendered_action_by_helper_soup = BeautifulSoup(rendered_action_by_helper, features="html.parser")

        name_field_value_1 = rendered_action_soup.form.select_one("#id_name").attrs["value"]
        name_field_value_2 = rendered_action_by_helper_soup.form.select_one("#id_name").attrs["value"]

        assert name_field_value_1 == name_field_value_2


def describe_handle_action():
    def it_sets_request_attrs(mocker, test_user):
        class TestAction(ViewActions):
            name = "test_action"
            embed_type = EmbedType.MODAL
            element = TestForm

            def handle(self, request, form, **kwargs):
                pass

        mock_handle = mocker.patch.object(TestAction, "handle")
        handle_action(TestAction(), request_attrs={"user": test_user})
        args = mock_handle.call_args[0]

        assert args[0].user == test_user

    @pytest.mark.parametrize(
        ("field", "initial_value"),
        [
            (forms.CharField(), "aaa"),
            (forms.CharField(widget=forms.Textarea()), "aaa"),
            (forms.DateField(), "2023-05-01"),
            (forms.BooleanField(), "on"),
            (forms.ChoiceField(choices=[("a", "A"), ("b", "B")]), "a"),
            (forms.ChoiceField(choices=[("a", "A"), ("b", "B")], widget=forms.RadioSelect()), "a"),
            (forms.MultipleChoiceField(choices=[("a", "A"), ("b", "B")]), ["a", "b"]),
        ],
    )
    def it_includes_all_input_types_in_post_data(mocker, field, initial_value):
        class TestForm(forms.Form):
            test_field = field

        class TestAction(ViewActions):
            name = "test_action"
            embed_type = EmbedType.MODAL
            element = TestForm

            def get_form_kwargs(self, request, FormClass, **kwargs):
                form_kwargs = super().get_form_kwargs(request, FormClass, **kwargs)
                form_kwargs["initial"]["test_field"] = initial_value
                return form_kwargs

            def handle(self, request, form, **kwargs):
                pass

        mock_handle = mocker.patch.object(TestAction, "handle")
        handle_action(TestAction())
        args = mock_handle.call_args[0]
        post_data = args[0].POST
        value = initial_value if isinstance(initial_value, list) else [initial_value]

        assert post_data.getlist("test_field") == value

    def it_updates_post_data_from_input(mocker):
        class TestForm(forms.Form):
            field_a = forms.CharField()
            field_b = forms.MultipleChoiceField(choices=[])

        class TestAction(ViewActions):
            name = "test_action"
            embed_type = EmbedType.MODAL
            element = TestForm

            def handle(self, request):
                pass

        mock_handle = mocker.patch.object(TestAction, "handle")
        handle_action(TestAction(), input={"field_a": "a", "field_b": ["a", "b"]})
        args = mock_handle.call_args[0]
        post_data = args[0].POST

        assert post_data.get("field_a") == "a"
        assert post_data.getlist("field_b") == ["a", "b"]

    def it_updates_post_files_from_input(mocker):
        class TestForm(forms.Form):
            field = forms.FileField()

        class TestAction(ViewActions):
            name = "test_action"
            embed_type = EmbedType.MODAL
            element = TestForm

            def handle(self, request, form, **kwargs):
                pass

        file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        mock_handle = mocker.patch.object(TestAction, "handle")
        handle_action(TestAction(), input={"field": file})
        args = mock_handle.call_args[0]
        files = args[0].FILES

        assert file.file.getvalue() == files.get("field").file.getvalue()

    def it_returns_success_url():
        class TestForm(forms.Form):
            field = forms.FileField()

        class TestAction(ViewActions):
            name = "test_action"
            embed_type = EmbedType.MODAL
            element = TestForm
            success_url = "/my_url"

            def handle(self, request, form, **kwargs):
                pass

        response = handle_action(TestAction())

        assert response.url == "/my_url"
