from crispy_forms.helper import FormHelper
from django.db.models import Model


def fk_to_model_fields(model: Model, fk_model: Model, fields=None):
    """
    Returns fields that are foreign keys to the specified fk_model
    """

    def is_fk_to_model_field(field):
        return (field.name in fields if fields else True) and (
            field.remote_field.model == fk_model if field.remote_field else False
        )

    return filter(is_fk_to_model_field, model._meta.fields)


def layout_insert_at_field(helper: FormHelper, index_field: str, new_field: str):
    """
    Inserts a field at the index of the `index_field` specified in the the layout
    of the FormHelper
    """
    indexes = helper[index_field].slice[0][0]
    layout_field = helper.layout
    for i in indexes[:-1]:
        layout_field = layout_field[i]
    layout_field.insert(indexes[-1], new_field)
