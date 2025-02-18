from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http.request import HttpRequest
from django.template.defaultfilters import title
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from dynpy_actions.actions import ModelViewActions
from dynpy_actions.enums import EmbedType
from dynpy_actions.forms import button_form_factory


class GenericCreateUpdateAction(ModelViewActions):
    """
    Generic action for CreateUpdate.
    """

    embed_type = EmbedType.MODAL
    allow_create_new = True

    def form_invalid(self, request, model_instance, form):
        self.get_error_message(request, model_instance, form)

    def form_valid(self, request, model_instance, form):
        self.get_success_message(request, model_instance, form)
        return form.save()

    def handle(self, request, form, **kwargs):
        model_instance = kwargs.get("model_instance")
        if form.is_valid():
            self.form_valid(request, model_instance, form)
        else:
            self.form_invalid(request, model_instance, form)

    def get_success_message(self, request, model_instance, form):
        """
        Default message for successful POST.
        '{Model name} Created/Updated Successfully'.
        """
        messages.success(
            request,
            f"{form.Meta.model._meta.verbose_name.capitalize()} Updated Successfully"
            if model_instance
            else f"{form.Meta.model._meta.verbose_name.capitalize()} Created Successfully",
        )

    def get_error_message(self, request, model_instance, form):
        """
        Default message for unsuccessful POST.
        '{Model name} not saved {Key of error} : {error}'
        i.e. Phone: Not a valid phone number
        Does not show key when the key is '__all__' (the key for all validation in form.clean())
        """
        error_str = mark_safe(f"<h5>{form.Meta.model._meta.verbose_name.capitalize()} not saved</h5>")
        for k, v in form.errors.items():
            error_str += mark_safe(
                f"<b>{f'{title(k)}:' if k != '__all__' else ''}</b> {strip_tags(v)}</br>"
            )
        messages.error(request, error_str)

    # Overridden methods from ViewActions
    def get_button_value(self, request: HttpRequest, **kwargs) -> str:
        """
        If creating button text is 'Add <model_verbose_name>'.
        If updating button text is 'Edit'.
        """
        model_instance = kwargs.get("model_instance")
        if model_instance:
            return "<i class='fa fa-edit'></i> Edit"
        else:
            return f"<i class='fa fa-plus'></i> Add {self.get_model_verbose_name()}"

    def get_modal_title(self, request: HttpRequest, **kwargs) -> str:
        """
        If creating title is 'Add <model_verbose_name>'.
        If updating title is 'Edit <model_verbose_name>'.
        """
        model_instance = kwargs.get("model_instance")
        title_prefix = "Edit" if model_instance else "Add"
        return f"{title_prefix} {self.get_model_verbose_name()}"

    def get_model_verbose_name(self):
        return self.get_form_class()._meta.model._meta.verbose_name

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class.submit_label = "Save"
        return form_class


class DeleteAction(ModelViewActions):
    element = button_form_factory(
        inner_html='<i class="fa fa-times"></i> Delete',
        button_kwargs={"css_class": "btn btn-sm btn-danger text-nowrap"},
    )
    embed_type = EmbedType.INLINE
    name = "delete"
    needs_confirmation = True
    pre_render = True

    def get_confirmation_text(self, request: HttpRequest, **kwargs) -> str:
        model_name = self.get_model_name(request, **kwargs)
        return f"Are you sure you want to delete this {model_name}?"

    def get_model_name(self, request: HttpRequest, **kwargs):
        if getattr(self, "model_name", None) is not None and self.model_name:
            return self.model_name
        else:
            return kwargs.get("model_instance")._meta.verbose_name.capitalize()

    def handle(self, request: HttpRequest, form, **kwargs):
        try:
            model_instance = kwargs["model_instance"]
        except (LookupError, ObjectDoesNotExist) as e:
            messages.error(request, f"Could not delete: {e}")
            return

        model_name = model_instance._meta.verbose_name.capitalize()
        model_instance.delete()
        messages.success(request, f"{model_name} Deleted Successfully")


class DeleteXAction(DeleteAction):
    element = button_form_factory(
        inner_html='<i class="fa fa-times fa-lg"></i>',
        button_kwargs={
            "css_class": "btn btn-link text-danger btn-sm text-nowrap",
            "data-toggle": "tooltip",
            "data-placement": "bottom",
            "title": "Delete",
        },
    )
    name = "delete_x"
