from bs4 import BeautifulSoup
from django.forms import Form, ModelMultipleChoiceField, MultipleChoiceField

from dynpy_forms.widgets import BootstrapMultiSelect


def describe_count_selected_text_data_attribue():
    def it_uses_items_as_the_default_for_non_model_choice_fields():
        class TestForm(Form):
            stuff = MultipleChoiceField(widget=BootstrapMultiSelect())

        form = TestForm()
        soup = BeautifulSoup(form.as_p(), features="html.parser")
        stuff_select = soup.select_one('select[name="stuff"]')
        assert stuff_select["data-count-selected-text"] == "{0} Items selected"

    def it_uses_value_of_item_name_plural_when_passed_in(django_user_model):
        class TestForm(Form):
            people = ModelMultipleChoiceField(
                queryset=django_user_model.objects.all(),
                widget=BootstrapMultiSelect(item_name_plural="people"),
            )
            stuff = MultipleChoiceField(widget=BootstrapMultiSelect(item_name_plural="stuff"))

        form = TestForm()
        soup = BeautifulSoup(form.as_p(), features="html.parser")
        people_select = soup.select_one('select[name="people"]')
        stuff_select = soup.select_one('select[name="stuff"]')
        assert people_select["data-count-selected-text"] == "{0} People selected"
        assert stuff_select["data-count-selected-text"] == "{0} Stuff selected"

    def it_uses_model_verbose_name_for_model_choice_field_by_default(django_user_model):
        verbose_name_plural = django_user_model._meta.verbose_name_plural

        class TestForm(Form):
            users = ModelMultipleChoiceField(
                queryset=django_user_model.objects.all(),
                widget=BootstrapMultiSelect(),
            )

        form = TestForm()
        soup = BeautifulSoup(form.as_p(), features="html.parser")
        users_select = soup.select_one('select[name="users"]')
        assert (
            users_select["data-count-selected-text"] == f"{{0}} {verbose_name_plural.title()} selected"
        )
