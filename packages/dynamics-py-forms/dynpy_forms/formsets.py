import uuid

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet, generic_inlineformset_factory
from django.forms.models import (
    BaseInlineFormSet,
    BaseModelFormSet,
    ModelForm,
    inlineformset_factory,
    modelformset_factory,
)
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe


class NestedFormsetMixin:
    """
    Formset mixin to override a formsets 'forms' property to set
    `form_tag = False` and `form_show_labels = False`.

    Overriding the defaults of 'form_tag' and 'show_header_row can
    be done in 'dynamic_formset_factory'
    """

    form_tag = True
    show_header_row = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A unique id is needed to keep the jquery.formset.js scoped to each forset individually
        self.id = f"{self.id}-{uuid.uuid4()}"

    @cached_property
    def forms(self):
        """
        Override a formsets 'forms' property to set `form_tag = False`
        and `form_show_labels = False`.
        """
        forms = super().forms
        for form in forms:
            if not hasattr(form, "helper"):
                form.helper = FormHelper()
            form.helper.form_tag = self.form_tag
            if self.show_header_row:
                form.helper.form_show_labels = False
        return forms


class NestedModelFormset(NestedFormsetMixin, BaseModelFormSet):
    pass


class NestedInlineFormset(NestedFormsetMixin, BaseInlineFormSet):
    pass


class NestedGenericInlineFormset(NestedFormsetMixin, BaseGenericInlineFormSet):
    pass


class DynModelFormset(NestedModelFormset):
    """Leave this class for backwards compatibility"""


def set_dynamic_formset_attrs(formset, **kwargs):
    """
    # ---------------------------------------------------------------------------- #
    #                     READ WARNING BELOW BEFORE USING                          #
    # ---------------------------------------------------------------------------- #

    ** Warning ** : When using multiple different formsets on a page, you need to set form_css_class,
                    prefix and id.
                    If using multiple of the same one on a page, you need to make sure form_css_class and
                    id (do not need a prefix if there is only one type of a formset on the page)
                    have a unique id (i.e using model_instance_id,
                    `form_css_class = form_css_class_{model_instance_id})`

    ** Note **    : jquery.formset.js needs to be loaded in the html template that is rendering the formset.


    """

    # Set whether the formset has <form> tags (defult to False for nested formsets, which is the primary usage)
    formset.form_tag = kwargs.get("form_tag", False)

    # These are used to render a header row with labels (this row is not repeated when another form row is added)
    formset.show_header_row = kwargs.get("show_header_row", False)

    # The key of 'label_classes' needs to be the name of the field and the values should be the classes (as a str)
    formset.label_classes = kwargs.get("label_classes", {})

    # The defaults are empty strings because these values are being passed to JS
    # and passing in None will be equated to 'None' by the JS.
    # Look in jquery.formset.js at the default options for explanations of these attrs

    # Needed by frontend to instantiate the formset
    formset.id = kwargs.get("id", "")

    formset.delete_text = kwargs.get(
        "delete_text",
        mark_safe(
            """
            <span class='text-danger btn btn-link mb-2'>
                <i class='fa fa-times'></i>
            </span>
        """
        ),
    )
    formset.form_css_class = kwargs.get("form_css_class", "")
    formset.item_name = kwargs.get("item_name", "")
    formset.is_repeatable = kwargs.get("is_repeatable", True)
    formset.confirmation_message = kwargs.get("confirmation_message", "Are you sure?")
    formset.removed = kwargs.get("removed", "")
    formset.added = kwargs.get("added", "")
    formset.show_labels_once = kwargs.get("show_labels_once", "")
    formset.prefix = kwargs.get("prefix", "form")
    formset.delete_container_class = kwargs.get("delete_container_class", "")
    formset.keep_field_values = kwargs.get("keep_field_values", "")
    formset.remove_last_add_form = kwargs.get("remove_last_add_form", "")
    formset.remove_last_add_form_unless_is_only_form = kwargs.get(
        "remove_last_add_form_unless_is_only_form", False
    )
    return formset


def dynamic_formset_factory(
    model, form, formset=DynModelFormset, extra=1, max_num=None, min_num=None, can_delete=False, **kwargs
):

    formset = modelformset_factory(
        model,
        form=form,
        extra=extra,
        max_num=max_num,
        min_num=min_num,
        can_delete=can_delete,
        formset=formset,
    )
    set_dynamic_formset_attrs(formset, **kwargs)
    return formset


dyn_formset_factory = dynamic_formset_factory  # Alias for backwards compatibility


def dynamic_inlineformset_factory(
    parent_model,
    model,
    form=ModelForm,
    formset=NestedInlineFormset,
    fk_name=None,
    extra=1,
    max_num=None,
    min_num=None,
    **kwargs,
):

    formset = inlineformset_factory(
        parent_model,
        model,
        form=form,
        formset=formset,
        fk_name=fk_name,
        extra=extra,
        max_num=max_num,
        min_num=min_num,
    )
    set_dynamic_formset_attrs(formset, **kwargs)
    return formset


def dynamic_generic_inlineformset_factory(
    model,
    form=ModelForm,
    formset=NestedGenericInlineFormset,
    fk_name=None,
    extra=1,
    max_num=None,
    min_num=None,
    **kwargs,
):
    formset = generic_inlineformset_factory(
        model,
        form=form,
        formset=formset,
        fk_name=fk_name,
        extra=extra,
        max_num=max_num,
        min_num=min_num,
    )
    set_dynamic_formset_attrs(formset, **kwargs)
    return formset


class ModelChoiceFieldMixin(forms.BaseFormSet):
    """
    Overload the ModelChoiceField querysets by a common queryset per
    field, with dummy .all() and .iterator() methods to avoid multiple
    queries when filling the (repeated) choices fields.
    """

    # Init the formset
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        model_choice_fields_qs = {}
        if len(self.forms) > 0:

            # Store querysets of modelchoicefields
            first_form = self.forms[0]
            for key in first_form.fields:
                if isinstance(first_form.fields[key], forms.ModelChoiceField):
                    model_choice_fields_qs[key] = first_form.fields[key].queryset

        # Django calls .queryset.all() before iterating over the queried objects
        # to render the select boxes. This clones the querysets and multiplies
        # the queries for nothing.
        # Hence, overload the querysets' .all() method to avoid cloning querysets
        # in ModelChoiceField. Simply return the queryset itself with a lambda function.
        # Django also calls .queryset.iterator() as an optimization which
        # doesn't make sense for formsets. Hence, overload .iterator as well.
        if model_choice_fields_qs:
            for qs in model_choice_fields_qs.values():
                qs.all = (
                    lambda local_qs=qs: local_qs
                )  # use a default value of qs to pass from late to immediate binding
                # (so that the last qs is not used for all lambda's)
                qs.iterator = qs.all

            # Apply the common (non-cloning) querysets to all the forms
            for form in self.forms:
                for key in model_choice_fields_qs:
                    form.fields[key].queryset = model_choice_fields_qs[key]
