from urllib.parse import urlencode

from django.urls import reverse


def reverseplus(viewname, urlconf=None, args=None, kwargs=None, current_app=None, params=None):
    url = reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None)
    query_string = urlencode(params)
    return f"{url}?{query_string}"
