import pytest
from django.db.models import CASCADE, CharField, ForeignKey, Model

from dynpy_forms.utils import fk_to_model_fields


@pytest.fixture()
def this_model(that_model):
    class OtherModel(Model):
        class Meta:
            app_label = "tests"

    class ThisModel(Model):
        fk_to_that_1 = ForeignKey(that_model, on_delete=CASCADE)
        fk_to_that_2 = ForeignKey(that_model, on_delete=CASCADE)
        fk_to_other = ForeignKey(OtherModel, on_delete=CASCADE)
        char_field = CharField()

        class Meta:
            app_label = "tests"

    return ThisModel


@pytest.fixture()
def that_model():
    class ThatModel(Model):
        class Meta:
            app_label = "tests"

    return ThatModel


def test_returns_fk_to_model_fields(this_model, that_model):
    fields = list(fk_to_model_fields(this_model, that_model))
    assert len(fields) == 2


def test_excludes_fk_to_model_fields_not_in_fields_list(this_model, that_model):
    fields = list(fk_to_model_fields(this_model, that_model, fields=["fk_to_that_1", "fk_to_other"]))
    assert len(fields) == 1
