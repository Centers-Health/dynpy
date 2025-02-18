import urllib.parse

from django import template
from django.utils.safestring import mark_safe
from dynpy_actions import constants
from dynpy_actions.helpers import serialize_kwargs, validate_action

register = template.Library()


@register.simple_tag(takes_context=True)
def render_action_template(context, action, **kwargs) -> str:
    """
    Returns the template for an action.
    """
    validate_action(context, action)
    request = context["request"]
    rendered_template = action.render_action(request, context, **kwargs)
    return mark_safe(rendered_template)


@register.simple_tag()
def render_kwargs_as_data_attributes(template_kwargs) -> str:
    """
    Takes a dictionary and renders it as data-attributes.
    """
    template_kwargs = serialize_kwargs(**template_kwargs)
    data_attributes = " ".join(
        f'data-action_{k} = "{urllib.parse.quote(v)}" ' for k, v in template_kwargs.items()
    )
    return mark_safe(data_attributes)


@register.simple_tag
def render_button_attributes(action) -> str:
    """
    Renders html attributes from a dict.
    Sets default class attributes.
    """
    button_attributes = action.button_attributes
    additional_classes = " ".join(action.additional_button_classes)
    button_attributes.setdefault("class", f"btn btn-primary btn-sm {additional_classes}")

    # The JS uses this attribute to load the action and set the onClick.
    if not action.pre_render:
        button_attributes["data-js-load-action-form"] = True

    attrs_str = ""
    for name, value in button_attributes.items():
        if value is not False:
            attrs_str += f" {name}"
        if value is not True:
            attrs_str += f'="{str(value)}"'
    return mark_safe(attrs_str)


@register.simple_tag(takes_context=True)
def render_hash(context, action, **kwargs) -> str:
    """
    Sets a url param to the action's hash. For this to work properly,
    the function requires the kwargs being used in the hash. By default
    this is just the model instance (for ModelViewActions). If
    get_hashing_list is overridden and the hash uses other kwargs, those
    will need to be passed into this template tag.
    """
    hash = action.get_hash(context.get("request"), **kwargs)
    return f"action_hash={urllib.parse.quote_plus(hash)}"


@register.filter()
def build_url_with_query(url, kwargs) -> str:
    serialized_kwargs = serialize_kwargs(**kwargs, _prefix=constants.ACTION_KWARGS_PREFIX)
    url += ("&" if urllib.parse.urlparse(url).query else "?") + urllib.parse.urlencode(serialized_kwargs)
    return url
