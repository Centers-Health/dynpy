from django import forms
from django.template import Template
from django.template.context import Context
from dynpy_forms.fields import FullObjectSelectField
from dynpy_forms.widgets import BootstrapSelect


def test_widget_renders_option_template_as_include(django_user_model):
    class TestForm(forms.Form):
        field = FullObjectSelectField(
            queryset=django_user_model.objects.all(),
            widget=BootstrapSelect(
                option_template="dynpy_forms/includes/dummy_include_template_for_testing.html",
                attrs={
                    "class": "selectpicker form-control ml-2 dss-select",
                },
            ),
        )

    django_user_model.objects.create(username="John")
    response = Template("{% load crispy_forms_tags %}{% crispy form %}").render(
        Context({"form": TestForm})
    )
    assert "This is a template for testing includes" in response


def test_widget_renders_option_template_as_plain_html(django_user_model):
    class TestForm(forms.Form):
        field = FullObjectSelectField(
            queryset=django_user_model.objects.all(),
            widget=BootstrapSelect(
                option_template="<h1 class='text-danger'>test html</h1>",
                attrs={
                    "class": "selectpicker form-control ml-2 dss-select",
                },
            ),
        )

    django_user_model.objects.create(username="John")
    response = Template("{% load crispy_forms_tags %}{% crispy form %}").render(
        Context({"form": TestForm})
    )
    assert "text-danger" in response
    assert "test html" in response
