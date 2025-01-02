import re
from typing import Optional

from bs4 import BeautifulSoup
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http.response import HttpResponseRedirect
from django.template import RequestContext
from django.test import RequestFactory
from django.utils.safestring import mark_safe

from dynpy_actions.actions import ViewActions
from dynpy_actions.helpers import deserialize_kwargs, serialize_kwargs


def display_action(
    action: ViewActions,
    view_context: Optional[dict] = None,
    request_attrs: Optional[dict] = None,
    action_kwargs: Optional[dict] = None,
):
    """
    Helper for testing the display of an action.

    Example:
    ```
    def test_my_action_display(test_user, test_model_instance):
       action = MyAction()
       action_html = display_action(
          action,
          request_attrs={"user": test_user},
          action_kwags={"model_instance": test_model_instance},
       )

    # Add asserts here...
    ```

    action_kwargs represents the kwargs passed into the action template tag.

    For example:
    ```{% render_action_template actions.test_action model_instance=user %}```
    can be tested like so:
    ```display_action(test_action, action_kwags={"model_instance": user})```
    """
    request = RequestFactory().get("/")
    view_context = view_context or {}
    request_attrs = request_attrs or {}
    action_kwargs = action_kwargs or {}

    # Add message middleware
    request.session = "session"
    messages = FallbackStorage(request)
    request._messages = messages

    for attr, value in request_attrs.items():
        setattr(request, attr, value)

    context = RequestContext(request, view_context)
    action.pre_render = True
    rendered_template = action.render_action(request, context, **action_kwargs)
    return mark_safe(rendered_template)


def handle_action(
    action: ViewActions,
    view_context: Optional[dict] = None,
    request_attrs: Optional[dict] = None,
    action_kwargs: Optional[dict] = None,
    input: Optional[dict] = None,
):
    """
    Helper for testing the handle method of an action.

    Example:
    ```
    def test_my_action_handle(test_user, test_model_instance, test_file):
       action = MyAction()
       action_html = handle_action(
          action,
          request_attrs={"user": test_user},
          action_kwags={"model_instance": test_model_instance},
          input={
            "field_a": "aaaa",
            "field_b": ["1", "2"],
            "field_c": "on",
            "field_d": test_file,
          }
       )

    # Add asserts here...
    ```

    action_kwargs represents the kwargs passed into the action template tag.

    For example:
    ```{% render_action_template actions.test_action model_instance=user %}```
    can be tested like so:
    ```display_action(test_action, action_kwags={"model_instance": user})```
    """
    action_kwargs = action_kwargs or {}

    action_html = display_action(
        action,
        view_context=view_context,
        request_attrs=request_attrs,
        action_kwargs=action_kwargs,
    )

    input = input or {}
    request_attrs = request_attrs or {}
    soup = BeautifulSoup(action_html, "html.parser")
    form = soup.find("form")
    form_action = form.get("action", "/")
    form_data = {}

    def update_dict_value(dict_, key, value):
        if key in dict_:
            if isinstance(dict_[key], list):
                dict_[key].append(value)
            else:
                dict_[key] = [dict_[key], value]
        else:
            dict_[key] = value

    for input_field in form.find_all("input", {"name": True}):
        name = input_field["name"]
        value = input_field.get("value", "")
        if input_field.get("type") in ["checkbox", "radio"]:
            if not input_field.has_attr("checked"):
                continue
            value = input_field.get("value", "on")

        update_dict_value(form_data, name, value)

    for textarea_field in form.find_all("textarea"):
        name = textarea_field["name"]
        text = textarea_field.get_text()
        # remove newline characters and spaces
        value = re.sub(r"[\\n\s]", "", text)
        update_dict_value(form_data, name, value)

    for select_field in form.find_all("select"):
        name = select_field["name"]
        for option in select_field.find_all("option", {"selected": True}):
            value = option.get("value", "")
            update_dict_value(form_data, name, value)

    for button_field in form.find_all("button", {"name": True}):
        name = button_field["name"]
        value = button_field.get("value", "")
        update_dict_value(form_data, name, value)

    # update with input
    for name, value in input.items():
        form_data[name] = value

    request_factory = RequestFactory()
    request = request_factory.post(form_action, data=form_data)

    # Add message middleware
    request.session = "session"
    messages = FallbackStorage(request)
    request._messages = messages

    for attr, value in request_attrs.items():
        setattr(request, attr, value)
    action_kwargs = (
        deserialize_kwargs(**serialize_kwargs(**action_kwargs))
        if not action.pre_render
        else action_kwargs
    )
    form = action.get_initialized_form(request, data=request.POST, files=request.FILES, **action_kwargs)
    return action.handle(request, form, **action_kwargs) or HttpResponseRedirect(
        action.get_success_url(request)
    )
