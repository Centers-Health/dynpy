import os
from os.path import splitext
from urllib.parse import quote, urljoin

from django import template
from django.conf import settings
from django.templatetags.static import PrefixNode
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(name="absolute_static")
def get_absolute_static_url(path):
    absolute_static_path = get_absolute_base_url(PrefixNode.handle_simple("STATIC_URL"))
    return urljoin(absolute_static_path, quote(path))


@register.simple_tag(name="absolute_url")
def get_reversed_absolute_base_url(path, *args, **kwargs):
    url = reverse(path, args=args, kwargs=kwargs)
    return get_absolute_base_url(url)


@register.simple_tag(name="base_url")
def get_absolute_base_url(path):
    absolute_base_url = PrefixNode.handle_simple("BASE_URL")
    return urljoin(absolute_base_url, quote(path))


@register.filter()
def env(value):
    return os.environ.get(value, None)


@register.simple_tag(takes_context=True)
def set_breakpoint(context):
    __import__("pdb").set_trace()


@register.filter
def get_extension(filename: str) -> str:
    """
    Returns the extension of a file.
    """
    try:
        stringlets = splitext(filename)
        return stringlets[1]
    except TypeError:
        return filename


@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr, None)


@register.filter
def get_dict_value(obj, attr):
    return obj.get(attr, None)


@register.simple_tag(takes_context=True)
def redirect_back(context, **kwargs):
    return f"?{urlencode({'redirect_back' : context['request'].get_full_path()})}"


@register.filter
def field_name_to_label(value):
    try:
        value = value.replace("_", " ").replace("  ", " ").strip()
        return value.title()
    except AttributeError:
        return value


@register.filter
def to_str(value):
    """converts int to string"""
    return str(value) if value else ""


@register.filter
def remove_underscores(value):
    try:
        return value.replace("_", " ")
    except AttributeError:
        return value


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context["request"].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d.urlencode()


@register.filter
def bool_to_check_or_x(value):
    if value:
        return mark_safe('<i class="fa fa-check-circle text-success"></i>')
    else:
        return mark_safe('<i class="fa fa-times-circle text-danger"></i>')


@register.inclusion_tag("dynpy/tawkto.html", takes_context=True)
def render_tawkto(context, manual_mode=True):
    request = context["request"]
    user = getattr(request, "user", None)
    prod_property = "https://embed.tawk.to/639be7e3daff0e1306dce787/1gko5qftd"
    test_property = "https://embed.tawk.to/65e9f6d38d261e1b5f6a3c19/1hocuob44"
    tawkto_embed_url = test_property if settings.DJANGO_ENV != "prod" else prod_property
    return {"manual_mode": manual_mode, "user": user, "tawkto_embed_url": tawkto_embed_url}


@register.simple_tag(takes_context=False)
def hash_hmac(data: str, key: str = "") -> str:
    import hashlib
    import hmac

    if key == "":
        key = settings.TAWK_TO_CHAT_KEY

    # Create a new HMAC object
    hash = hmac.new(bytes(key, "latin-1"), msg=bytes(data, "latin-1"), digestmod=hashlib.sha256)

    # Print the hexadecimal representation of the HMAC
    return hash.hexdigest()
