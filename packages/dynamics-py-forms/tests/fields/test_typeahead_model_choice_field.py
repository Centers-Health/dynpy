import pytest
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.forms import Form

from dynpy_forms.fields import TypeAheadModelChoiceField


# Helpers
class DummyForm(Form):
    payor = TypeAheadModelChoiceField(
        queryset=get_user_model().objects.none(),
        query_name="test",
        field_for_label="name",
    )


@pytest.mark.django_db()
def test_validates_against_all_of_model_objects(django_user_model):
    user = django_user_model.objects.create(username="Test")

    form = DummyForm(data={"payor": str(user.pk)})
    assert form.is_valid()


@pytest.mark.django_db()
def test_uses_field_for_label_for_option_text(django_user_model):
    user = django_user_model.objects.create(username="Test")

    form = DummyForm(initial={"payor": user.pk})
    soup = BeautifulSoup(form.as_p(), features="html.parser")

    assert str(user) in soup.find("option", selected=True, value=user.pk).text


@pytest.mark.django_db()
def test_uses_str_object_for_option_text_when_field_for_label_is_not_set(
    django_user_model,
):
    user = django_user_model.objects.create(username="Test")

    class TestFormWithNoFieldForLabel(Form):
        user_field = TypeAheadModelChoiceField(
            queryset=django_user_model.objects.none(),
            query_name="test",
        )

    form = TestFormWithNoFieldForLabel(initial={"user_field": user.pk})
    soup = BeautifulSoup(form.as_p(), features="html.parser")

    assert str(user) in soup.find("option", selected=True, value=user.pk).text


def test_widget_uses_query_name():
    soup = BeautifulSoup(DummyForm().as_p(), features="html.parser")
    query_script = soup.find("script")
    assert "searchQueryName = 'test'" in query_script.text
