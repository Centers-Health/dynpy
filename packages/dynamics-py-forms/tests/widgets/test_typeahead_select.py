import pytest
from bs4 import BeautifulSoup
from django.forms import CharField, Form, ModelChoiceField

from dynpy_forms.widgets import TypeAheadSelect


def test_uses_correct_query():
    widget_html = TypeAheadSelect(query_name="someQuery").render("some_field", None)
    soup = BeautifulSoup(widget_html, features="html.parser")
    query_script = soup.find("script")
    assert "searchQueryName = 'someQuery'" in query_script.text


def test_updates_choices_to_have_initial_value_for_char_field():
    class TestForm(Form):
        text = CharField(widget=TypeAheadSelect(query_name="someQuery"))

    form = TestForm(initial={"text": "abc"})
    soup = BeautifulSoup(form.as_p(), features="html.parser")
    assert soup.find("option", selected=True, value="abc")


@pytest.mark.django_db()
def test_updates_queryset_to_have_initial_value_for_model_field(django_user_model):
    user = django_user_model.objects.create(username="test")

    class TestForm(Form):
        payor = ModelChoiceField(
            queryset=django_user_model.objects.none(),
            widget=TypeAheadSelect(query_name="someQuery"),
        )

    form = TestForm(initial={"payor": user.pk})
    soup = BeautifulSoup(form.as_p(), features="html.parser")

    assert soup.find("option", selected=True, value=user.pk)
