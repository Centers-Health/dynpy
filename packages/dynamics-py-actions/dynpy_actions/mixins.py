from copy import copy
from typing import Dict, List

from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect
from django.template.defaultfilters import title
from django.utils.html import strip_tags

from dynpy_actions import constants
from dynpy_actions.actions import ModelViewActions, ViewActions
from dynpy_actions.exceptions import AsyncConfirmNotDefinedException
from dynpy_actions.helpers import deserialize_kwargs, flatten_kwargs


class ViewActionsMixin:
    """
    Mixin for actions that inserts them into the context
    and handles their GET and POST.

    Mixin to be added to a View.
    """

    actions: List[ViewActions]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create dict out of actions list; {action_name:action}
        actions_dict = {}
        for action in self.actions:
            actions_dict[action.name] = action
        context["actions"] = actions_dict

        return context

    def get(self, request, *args, **kwargs):
        """
        GET for the action. Checks for the action, if there is
        no action then it calls the parents GET which is the views
        GET. If there is an action then it returns the form for the
        action.
        """
        # The name is action_action__name because the key name is
        # action__name (see get_context_data in actions.py) and
        # 'action_' gets appended to all action kwargs.
        action_name = request.GET.get("action_action__name", None)
        if action_name:
            action = next(a for a in self.actions if a.name == action_name)
            if action:
                action.view = self
                flattened_kwargs = flatten_kwargs(**request.GET)
                kwargs.update(flattened_kwargs)
                view_context = {}
                if action.get_view_context:
                    super().get(request, *args, **kwargs)
                    view_context = self.get_context_data(**kwargs)
                return action().render_form(request, view_context, **kwargs)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        POST for the action. Checks for the action, if there is
        no action then it calls the parents POST which is the views
        POST. If there is an action then first it runs validation on
        the form. If the validation fails it returns the errors. If
        it passes then the action's handle function is called.
        """

        action_name = request.GET.get("action_action__name", None) or request.POST.get(
            "action_name", None
        )
        if action_name:
            action_class = next(a for a in self.actions if a.name == action_name)
            if action_class:
                action_instance = action_class()
                action_instance.view = self
                flattened_kwargs = flatten_kwargs(**request.GET)
                deserialized_kwargs = deserialize_kwargs(
                    _prefix=constants.ACTION_KWARGS_PREFIX,
                    **{
                        k: v
                        for k, v in flattened_kwargs.items()
                        if k.startswith(constants.ACTION_KWARGS_PREFIX)
                    },
                )
                form = action_instance.get_initialized_form(
                    request, request.POST, request.FILES, **deserialized_kwargs
                )

                # For validating the form asynchronously and adding async confirmation messages
                async_validate = request.POST.get("validate")
                async_confirm = request.POST.get("confirm")

                if async_validate or async_confirm:
                    response_data = {"success": True}
                    if async_validate:
                        response_data.update(
                            action_instance.async_validate(request, form, **deserialized_kwargs)
                        )
                    if response_data.get("success") is True and async_confirm:
                        response_data["message"] = self._get_confirmation_message(
                            request, action_instance, form, **deserialized_kwargs
                        )

                    return JsonResponse(response_data)
                response = action_instance.handle(request, form, **deserialized_kwargs)

                return response or HttpResponseRedirect(action_instance.get_success_url(request))
        return super().post(request, *args, **kwargs)

    def _get_confirmation_message(self, request, action_instance, form, **kwargs):
        if not getattr(action_instance, "async_confirm", None):
            raise AsyncConfirmNotDefinedException

        return action_instance.async_confirm(request, form, **kwargs) or ""


class AutoFillFormFromKwargsMixin:
    """
    Auto fills form fields with the kwargs from the template tag.
    If the field in the form matches the key of the kwarg it
    will be auto set to the value.

    i.e. If  this kwarg is passed in 'user=John Smith' and the form
    has a field 'user', that field will initially be set to
    'John Smith'.

    Mixin to be added to an action.
    """

    def get_form_kwargs(self, request: HttpRequest, FormClass, **kwargs) -> Dict:
        form_kwargs = super().get_form_kwargs(request, FormClass, **kwargs)
        form_class_fields = self.get_form_class().base_fields

        # Don't set model_instance field to the model_instance (this is already
        # done in actions.py using a serializer, doing it here will cause a bug
        # because it won't be serialized)
        kwargs.pop("model_instance", None)
        for key, value in kwargs.items():
            if key in form_class_fields:
                form_kwargs["initial"][key] = value

        return form_kwargs


class FormsetMixin:
    """
    Mixin for actions to supply functionality for formsets.

    To use, Add FormsetMixin to the action and set the formsets attr on the action.

    Currently only helps with async validate.
    TODO: Helpers for get_context_data and for handle

    To add kwargs to the formset (ie a prefix), override the get_{name}_kwargs
    function, where name is the key in formsets dict and return a dict from that
    function.
    ie
        ```
        def get_my_formset_kwargs(self, request, model_instance) -> dict:
            return {"prefix": "test_formset"}
        ```

    Params:
           formsets: Takes in a dict where the key is a meaningful name
                     for the formset and the value is the formset class.
                     The name(key) is used for the kwargs function.
    """

    formsets: dict  # {name: formset_class} ie {'my_formset': formset_class}

    def async_validate(self, request, form, **kwargs) -> Dict:
        data = request.POST
        files = request.FILES

        model_instance = self.get_model_instance(request) if isinstance(self, ModelViewActions) else None

        instantiated_formsets = self._get_instantiated_formsets(data, files, model_instance, request)

        if form.is_valid() and self._formsets_are_valid(instantiated_formsets):
            return {"success": True, "errors": {}}

        errors = copy(form.errors)
        for formset in instantiated_formsets:
            errors.update(self._get_formset_errors(formset))
        return {"success": False, "errors": errors.get_json_data()}

    def _get_formset_errors(self, formset) -> dict:
        """
        Build error dict so that the key matches the name of the field.
        ie form-0-id
        """
        errors = {}
        for index, error in enumerate(formset.errors):
            for field, error_message in error.items():
                errors[f"{formset.prefix}-{index}-{field}"] = error_message
        return errors

    def _get_instantiated_formsets(self, data, files, model_instance, request):
        formsets = []
        for name, formset_class in self.formsets.items():
            kwargs_fn = getattr(self, f"get_{name}_kwargs", None)
            kwargs = (
                kwargs_fn(
                    request,
                    model_instance,
                )
                if kwargs_fn
                else {}
            )
            formsets.append(formset_class(data, files, **kwargs))
        return formsets

    def _formsets_are_valid(self, instantiated_formsets):
        return all(formset.is_valid() for formset in instantiated_formsets)

    def get_formset_error_message(self, formset):
        """
        This function helps set up the synchronous error message toast
        """
        error_body = ""
        non_form_errors = ""
        form_name = formset.form._meta.model._meta.verbose_name
        error_title = f"<h6 class='mt-2 mb-0'><b>{title(form_name)} Errors:</b></h6>"
        for form_errors in formset.errors:
            for k, v in form_errors.items():
                error_body += f"""
                                <div class='ml-2'>
                                    <b>{f'{title(k.replace("_"," "))}:' if k != '__all__' else ''}</b>
                                        {strip_tags(v)}
                                    </br>
                                </div>
                            """
        for non_form_error in formset.non_form_errors():
            non_form_errors += f"""
                                <div class='ml-2'>
                                   {non_form_error}
                                    </br>
                                </div>
                            """
        return error_title + error_body + non_form_errors if error_body or non_form_errors else ""
