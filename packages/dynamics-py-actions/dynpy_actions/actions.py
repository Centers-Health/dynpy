import hashlib
import inspect
import uuid
import warnings
from itertools import cycle
from typing import Dict, List, Union

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django import forms
from django.db.models.base import Model
from django.forms import fields
from django.forms.widgets import (
    CheckboxInput,
    CheckboxSelectMultiple,
    FileInput,
    HiddenInput,
    RadioSelect,
)
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse

from dynpy_actions.enums import EmbedType, ModalSize
from dynpy_actions.exceptions import ConflictingConfirmationsException, TargetNotSpecifiedException
from dynpy_actions.helpers import deserialize_kwargs, serialize_args, serialize_kwargs


class ViewActions:
    """
    Class to add actions to any view. Actions can be rendered
    inline or as a modal. An action can consist
    of an entire form or just a single form field.

    If need actions to be tied to a model_instance use ModelViewActions
    below.

    Attributes:
        _counter: Generator to create unique id for every action.
        element: The form / form field that will be rendered
        embed_type: "Inline" or "Modal" or "Base" or "Target" ("Base" is mapped to use the
                    "Inline" template)
        name: the name For the action, needed to render out the action
        needs_confirmation: If true will prompt the user before submitting the action
        confirmation_text: The text of the prompt
        button_value: Text of the button, can be raw html
        button_attributes: Dictionary of html attributes for the button
        additional_button_classes: List of additional css classes to be applied to the button
        modal_title: Title displayed on the modal, can be raw html
        modal_size: Class that controls the modal size (width)
        pre_render: If false will load the form asynchronously
        autosubmit: If True will autosubmit the form onchange
        async_validatation: If true will validate the action asynchronously
        async_confirmation: If true will add an async confirmation prompt to the form on submit
                            **Note** : Cannot use both confirmation_message and async_confirmation on the same
                                       action
        validate_on: Event that async validation will trigger on. i.e 'change', 'input', 'submit'
        target_elem_id: Id of html element where a target action will render the form
        target_trigger_on: event trigger of a target action. i.e 'click', 'mouseover, 'dblclick' etc.
        template: Template that will be rendered in the target. To have a close button on your
                  target action, define an element with a class of close-btn.
        form_template: Template to be used for the form. Can extend
                       "dynpy_actions/action_generic_base_form.html" and override
                        specific blocks.
        callback: name of callback function that is defined globally in the js window
        modal_target: selector of html element where a modal action will render the form. Uses
                      one modal instead of using the one from the modal template, which creates
                      a separate modal inline for every action
        force_initial_fields: List of fields that will force the initial values on the form. Can set it to
                              "__all__" to force all initial values on the form that are in the kwargs.

    How To Use:
        1. Create an action that inherits ViewActions.
           Implement the handle method.
           Set the attributes that are needed, this can be in one of two ways.
           1. Statically, via the static fields on the class.
           2. Dynamically, via the get_<attr> functions which should return the value for the attribute.
        2. Add ViewActionsMixin to the view that actions are being added to.
        3. Give a list of actions to that view. i.e. actions = [action]
        4. In the template load the actions_tags template tag.
        5. In the template render the action by using the template tag.
           The template tag takes the action and **kwargs.
           i.e. {% render_action_template  actions.actionName model_instance=object %}
           actions.actionName is the action that needs to be rendered
           and object is a kwarg
        6. If using a target action, a target element needs to be created for the
           action to render the form.
           i.e <div id='target_div'></div>

           **Note**: A target action just renders the data-attributes. They will be rendered in
                     the element that the template tag is used in.

           **Warning**: Do not use hyphens in the **kwargs key names because JavaScript
                        will change the keys with hyphens to camel case.

           **Note**: The template tag does not support passing in a list as a **kwarg.
                     See  https://valmardynamics.atlassian.net/browse/DYN-862
    """

    _counter = cycle((i for i in range(100_000)))

    element: Union[forms.Form, forms.Field]
    embed_type: EmbedType
    name: str
    needs_confirmation: bool = False
    confirmation_text: str = "Are you sure you want to do this?"
    button_value: str = ""
    button_attributes: dict = None
    additional_button_classes: list = None
    modal_title: str = ""
    modal_size: ModalSize = ModalSize.DEFAULT
    pre_render: bool = False
    autosubmit: bool = False
    async_validation = True
    async_confirmation = False
    validate_on: str = "submit"
    success_url: str = None
    target_elem_id: str = ""
    target_trigger_on: str = "click"
    template: str = ""
    get_view_context: bool = False
    form_template: str = "dynpy_actions/action_generic_base_form.html"
    callback: str = None
    modal_target: str = ""
    force_initial_fields: list = None

    def __init__(self) -> None:
        # Unique id for every action.
        self._id = next(self._counter)

        self.button_attributes = self.button_attributes or {}
        self.additional_button_classes = self.additional_button_classes or []
        self.force_initial_fields = self.force_initial_fields or []

    class ActionBaseForm(forms.Form):
        """
        Base form for actions that has the action_name.
        """

        submit_label = "Submit"

        action_name = forms.CharField(widget=forms.HiddenInput())

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.form_tag = False
            self.helper.layout = self.get_form_layout()

        def get_form_layout(self):
            """
            Returns the form's layout.
            Override this method in the form (aka the element of the action)
            to change the layout.
            """
            return Layout(*self.fields.keys(), self.get_form_action())

        def get_submit_label(self):
            return self.submit_label

        def get_form_action(self):
            """
            Returns the form's submit button.
            Override this method in the form (aka the element of the action)
            to change just the submit button.

            WARNING: When overriding this function do NOT name the
            button (1st parameter) submit.
            """
            if self.autosubmit:
                return

            return ButtonHolder(
                Submit(
                    "submit-btn",  # WARNING: Do not name 'submit'.
                    self.get_submit_label(),
                    css_class="btn btn-primary float-right mb-2",
                ),
            )

    def get_form_class(self):
        """
        Return the class of the form for the action
        """
        if isinstance(self.element, fields.Field):

            class NewForm(self.ActionBaseForm):
                input = self.element
                autosubmit = self.autosubmit

        elif issubclass(self.element, forms.BaseForm):

            class NewForm(self.element, self.ActionBaseForm):
                input = None
                autosubmit = self.autosubmit

        return NewForm

    def get_initialized_form(
        self,
        request: HttpRequest,
        data=None,
        files=None,
        **kwargs,
    ) -> forms.Form:
        """
        Return a form instance for the action with initial defaults.
        """
        FormClass = self.get_form_class()
        form_kwargs = self.get_form_kwargs(request, FormClass, **kwargs)
        initialized_form = FormClass(data, files, **(form_kwargs or {}))
        if self.force_initial_fields and request.method == "POST":
            initialized_form.data = self.force_initial_values(initialized_form, **kwargs)
        return self.assign_unique_ids_for_widgets(initialized_form)

    def force_initial_values(self, initialized_form, **kwargs):
        form_data = initialized_form.data.copy() if initialized_form.data else {}
        for field in self.force_initial_fields:
            form_data[field] = initialized_form.initial[field]
        return form_data

    def get_force_initial_fields(self, request, **kwargs):
        return (
            [key for key in kwargs.keys()]
            if self.force_initial_fields == "__all__"
            else self.force_initial_fields
        )

    def assign_unique_ids_for_widgets(self, form):
        """
        This is needed for when multiple of the same action are asynchronously
        loaded on a page since this causes there to be conflicting ids. This is
        an issue for certain widgets and causes them to work unexpectedly.
        """
        widgets_that_require_unique_ids = (CheckboxInput, CheckboxSelectMultiple, RadioSelect, FileInput)
        for _, field in form.fields.items():
            if isinstance(field.widget, widgets_that_require_unique_ids):
                field.widget.attrs["id"] = f"id-{uuid.uuid4()}"
        return form

    def render_form(self, request: HttpRequest, view_context, **kwargs) -> HttpResponse:
        """
        FOR ASYNC (pre-render=False).
        Returns just the form, not the entire template
        i.e. Does not return the entire modal.
        """

        # Target actions can have a template instead of just a form.
        if self.embed_type == EmbedType.TARGET and self.template:
            template = self.template
        else:
            template = self.form_template

        deserialized_kwargs = deserialize_kwargs(**kwargs)
        self._set_all_attributes(request, **deserialized_kwargs)
        form = self.get_initialized_form(request, **deserialized_kwargs)

        context = {
            "view_context": view_context,
            **self.get_context_data(request, form, **deserialized_kwargs),
        }

        return TemplateResponse(request, template, context)

    def render_action(self, request: HttpRequest, view_context, **kwargs) -> str:
        """
        Returns the template for the action.
        """
        self._set_all_attributes(request, **kwargs)

        # map the "Base" type to use the "inline" template.
        # "Base" type should not be confused with action_generic_base_form.html
        template_map = {
            EmbedType.INLINE: "inline",
            EmbedType.BASE: "inline",
            EmbedType.MODAL: "modal",
            EmbedType.TARGET: "target",
        }
        template = f"dynpy_actions/action_generic_{template_map[self.embed_type]}_form.html"

        form = self.get_initialized_form(request, **kwargs) if self.pre_render else None

        context = {
            "view_context": view_context.flatten(),
            **self.get_context_data(request, form, **kwargs),
        }

        return render_to_string(
            template,
            context,
            request=request,
        )

    def handle(self, request, form, **kwargs) -> HttpResponse:
        """
        Placeholder - must be overwritten when subclassing;
        dictates what should happen on POST.
        """
        raise NotImplementedError('subclasses of ViewActions must implement the "handle" method.')

    def get_form(self, model_instance=None, data=None, files=None):
        """
        Can be used to return the bound form.
        Meant for action.handle method, to get the form with post data filled
        """
        form_kwargs = {}
        FormClass = self.get_form_class()

        if issubclass(FormClass, forms.BaseModelForm):
            form_kwargs.setdefault("instance", model_instance)
        return FormClass(data, files, **form_kwargs)

    def _set_all_attributes(self, request: HttpRequest, **kwargs):
        members = inspect.getmembers(self.__class__, lambda a: not (inspect.isroutine(a)))
        attributes = [a for a in members if not (a[0].startswith("__") and a[0].endswith("__"))]
        for attribute in attributes:
            attr_name = attribute[0]
            attr = getattr(self, attr_name)
            func = getattr(self, "get_" + attr_name, None)
            setattr(self, attr_name, func(request, **kwargs) if func else attr)

        if self.async_confirmation is True and self.needs_confirmation is True:
            raise ConflictingConfirmationsException(self)

    def get_context_data(self, request: HttpRequest, form, **kwargs) -> Dict:
        """
        Sets the context that is passed into the template.
        """
        # There are 2 underscores in these keys just in case a field on the
        # form has the name 'action_name' or 'action_id'. If the
        # kwargs key below matches the name of the field on the form and
        # the action is using AutoFIllFromFormKwargsMixin then there
        # would be errors.

        kwargs["action__name"] = self.name
        kwargs["action__id"] = f"{self.name}_{self._id}"
        kwargs["action__hash"] = self.get_hash(request, **kwargs)
        kwargs["action__modal_target"] = self.modal_target
        kwargs["action__modal_title"] = self.modal_title
        kwargs["action__modal_size"] = self.modal_size.value

        # If embed type=target check if target is set. If not raise exception
        # else put the target into the kwargs.
        if self.embed_type == EmbedType.TARGET:
            if not self.target_elem_id:
                raise TargetNotSpecifiedException()
            kwargs["action__target_elem_id"] = self.target_elem_id
            kwargs["action__target_trigger_on"] = self.target_trigger_on

        return {
            "action": self,
            "form": form,
            "action_kwargs": kwargs,
        }

    def get_form_kwargs(self, request: HttpRequest, FormClass, **kwargs) -> Dict:
        """
        Sets the **kwargs that are passed into the form.
        Can  override to dynamically customize the form **kwargs.
        i.e. Can set initial values.
        """
        form_kwargs = {}
        form_kwargs.setdefault("initial", {"action_name": self.name})
        return form_kwargs

    def async_validate(self, request, form, **kwargs) -> Dict:
        """
        Runs the action's form validation and returns a JSON
        response with the form errors. This function is used
        for ASYNCHRONOUS validation.
        """

        success = False
        if form.is_valid():
            success = True
        return {"success": success, "errors": form.errors.get_json_data()}

    def get_success_url(self, request: HttpRequest, **kwargs) -> str:
        if self.success_url is not None:
            return self.success_url
        else:
            return request.headers.get("referer") or ""

    def get_button_value(self, request: HttpRequest, **kwargs) -> str:
        """
        Returns the button_value. Can override this method
        to generate dynamic text for the button (can be raw html).
        Has access to the request and all **kwargs that were passed
        into the template tag.
        """
        modal_button_value = getattr(self, "modal_button_value", None)
        popover_button_value = getattr(self, "popover_button_value", None)
        get_modal_button_value = getattr(self, "get_modal_button_value", None)
        get_popover_button_value = getattr(self, "get_popover_button_value", None)

        if callable(get_modal_button_value):
            warnings.warn(
                "get_modal_button_value() is deprecated use get_button_value() instead",
                PendingDeprecationWarning,
            )
            return get_modal_button_value(request, **kwargs)

        if callable(get_popover_button_value):
            warnings.warn(
                "get_popover_button_value() is deprecated use get_button_value() instead",
                PendingDeprecationWarning,
            )
            return get_popover_button_value(request, **kwargs)

        if modal_button_value:
            warnings.warn(
                "modal_button_value is deprecated use button_value instead",
                PendingDeprecationWarning,
            )
            return modal_button_value

        if popover_button_value:
            warnings.warn(
                "popover_button_value is deprecated use button_value instead",
                PendingDeprecationWarning,
            )
            return popover_button_value

        return self.button_value

    def get_hash(self, request: HttpRequest, **kwargs) -> str:
        """
        Sets a hash for each action. By default, only the action name is used
        in the hash.
        """
        hashable_string = self.name
        stringified_args = serialize_args(*self.get_hashing_list(request, **kwargs))
        for item in stringified_args:
            hashable_string += item
        hasher = hashlib.sha256()
        string_as_bytes = str.encode(hashable_string)
        hasher.update(string_as_bytes)
        return hasher.hexdigest()

    def get_hashing_list(self, request: HttpRequest, **kwargs) -> List:
        """
        Returns a list of args to be used in the hashing.
        """
        return []


class ModelViewActions(ViewActions):
    """
    A subclass of ViewActions. ModelViewActions is an action that
    is tied to a model instance. The form will be prefilled with
    an instance and a model_instance_id field that will be set
    to the  model instance PK.

    An additional attribute of ModelViewActions:
        allow_create_new: If True will allow new model instances to be created.
                          This is a safety setting so that new elements aren't accidentally created.
                          This flag lets you override that behavior intentionally
    How To Use:
        1. Same as ViewActions EXCEPT ModelViewActions requires
           model_instance to be passed in as a kwarg. This model_instance
           is the instance that the action will be tied to.
        2. If the action is being used to **create** model_instances then
           model_instance will not be required.

    If using an action and need to set an additional field on the form.
    i.e. a foreign key. See AutoFillFormFromKwargsMixin in actions/mixins.py
    """

    allow_create_new: bool = False

    def get_form_class(self):
        """
        ModelViewActions adds model_instance_id and model_instance to the form
        and sets it to not be required if allow_create_new is True.
        """
        NewForm = super().get_form_class()
        NewForm.base_fields["model_instance_id"] = forms.CharField(widget=HiddenInput())
        NewForm.base_fields["model_instance"] = forms.CharField(widget=HiddenInput())
        if self.allow_create_new:
            NewForm.base_fields["model_instance_id"].required = False
            NewForm.base_fields["model_instance"].required = False

        return NewForm

    def get_form_kwargs(self, request: HttpRequest, FormClass, **kwargs) -> Dict:
        """
        ModelViewActions populates model_instance_id and model_instance serialized.
        Can  override to dynamically customize the form **kwargs.
        i.e. Can set initial values.
        """
        form_kwargs = super().get_form_kwargs(request, FormClass, **kwargs)
        if kwargs:
            model_instance = kwargs.get("model_instance", None)
            if model_instance:
                form_kwargs["initial"] = serialize_kwargs(
                    action_name=self.name,
                    model_instance_id=model_instance.pk,
                    model_instance=model_instance,
                )
                if issubclass(FormClass, forms.BaseModelForm):
                    form_kwargs.setdefault("instance", model_instance)

        return form_kwargs

    def get_model_instance(self, request: HttpRequest) -> Model:
        """
        ModelViewActions deserializes model instance from model_instance field.
        Useful for the action handle method to gain access to the model instance.
        """
        data = request.POST
        serialized_model_instance = data.get("model_instance")
        if not serialized_model_instance:
            return
        else:
            return deserialize_kwargs(model_instance=serialized_model_instance)["model_instance"]

    def get_hashing_list(self, request: HttpRequest, **kwargs) -> List:
        """
        ModelViewActions by default adds the model instance to the hashing.
        """
        return [kwargs.get("model_instance", "")]
