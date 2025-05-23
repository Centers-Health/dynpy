import importlib
from functools import reduce

from django import template
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

register = template.Library()


def load_app_config():
    app_config = {}

    if config_path := getattr(settings, "NAVBAR_CONFIG_PATH", None):
        try:
            config_module = importlib.import_module(config_path)
            app_config = getattr(config_module, "app_config", {})
        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            raise ImportError(
                f"Could not load app config from {config_path}. "
                "Ensure the module exists and has an 'app_config' attribute."
            ) from e
    return app_config


@register.filter
def get_app_config(app_name: str):
    return load_app_config().get(app_name, {})


@register.filter
def is_active_navbar_dropdown(dropdown_nav_item: dict, current_url_name: str) -> bool:
    # Return True if a given url name matches any of the url names under a given navbar dropdown item
    # Otherwise return False
    items = list(dropdown_nav_item["items"])
    for item in items:
        if item.get("url_name") == current_url_name:
            return True
        elif "items" in item:
            items += item["items"]
    return False


@register.filter
def has_administration_access(user):
    return user.is_superuser or user.is_staff


@register.simple_tag(takes_context=True)
def user_passes_item_permission(context, item):
    if "permissions" not in item:
        return True
    elif isinstance(item["permissions"], bool):
        return item["permissions"]
    elif isinstance(item["permissions"], list):
        user = context["request"].user
        return reduce(lambda curr, prev: user.has_perm(curr) and prev, item["permissions"], True)
    else:
        return item["permissions"](context["request"].user)


@register.simple_tag(takes_context=True)
def nav_item_url(context, item):
    # Returns a url from a nav item
    url_name = item["url_name"]
    if url_name.startswith("http"):
        return url_name
    if callable(url_name):
        url_name = url_name(context["request"].user)
    url_params = item.get("url_params", {})
    return reverse(url_name) + "?" + urlencode(url_params)


@register.simple_tag
def get_toasts_delay_time(message):
    """
    Returns the amount of time the toast stays open.
    Calculated by multiplying the number of words by 1/2 a second
    Minimum time of delay is 3 seconds.
    """
    message_str = str(message)
    word_count = len(message_str.split())
    delay = word_count * 500
    return delay if delay > 3000 else 3000


@register.filter
def user_display(user):
    if not isinstance(user, AbstractUser):
        return user
    return render_to_string(
        "dynpy_ui/includes/user_card.html",
        {"user": user, "placeholder": mark_safe('<i class="fa fa-user"></i>')},
    )
