import pytest
from bs4 import BeautifulSoup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Field, Layout, Row
from crispy_forms.utils import render_crispy_form
from django.forms import CharField, DateTimeField, Form

from dynpy_forms.utils import layout_insert_at_field


@pytest.mark.parametrize(
    "layout",
    [
        Layout(
            Field("some_text"),
            Row(Column(Div(Field("some_other_text")), Div(Field("date_time")))),
        ),
        Layout(
            Div(Field("date_time")),
            Div(Field("some_other_text")),
            Div(Field("some_text")),
        ),
        Layout(Row("some_text"), Row(Column("date_time")), Row(Column("some_other_text"))),
        Layout("some_text", "some_other_text", "date_time"),
    ],
)
def test_inserts_at_position_of_field(layout):
    class MyForm(Form):
        some_text = CharField()
        some_other_text = CharField()
        date_time = DateTimeField()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = layout

    form = MyForm()
    _slice = form.helper["date_time"].slice[0][0]
    form.fields["new_field"] = CharField()
    layout_insert_at_field(form.helper, "date_time", "new_field")
    assert form.helper["new_field"].slice[0][0] == _slice
    form_html = render_crispy_form(form)
    soup = BeautifulSoup(form_html, features="html.parser")
    date_time_input = soup.find("input", id="id_date_time")
    new_field_input = soup.find("input", id="id_new_field")
    inputs = soup.find_all("input")
    date_time_input_index = inputs.index(date_time_input)
    assert inputs[date_time_input_index - 1] == new_field_input
