# source: https://gist.github.com/LouisdeBruijn/d638142e8fca50734853a97e4f6dc74f#file-user_passes_test-py
# from article: https://medium.com/better-programming/custom-view-decorators-in-django-af50ea9b3994

from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect, resolve_url

default_message = "Unauthorised action."
unauthenticated_message = "User already logged in."


def user_passes_test(test_func, redirect_field_name=REDIRECT_FIELD_NAME, message=default_message):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)

            # If the user is logged in this means the user does not have access to the
            # requested view so redirect to the login redirect URL otherwise redirect to the login page
            if request.user.is_authenticated:
                messages.add_message(request, messages.ERROR, message)
                return redirect(resolve_url(settings.LOGIN_REDIRECT_URL))

            resolved_redirect_url = resolve_url(settings.LOGIN_URL)
            current_path_for_next = request.build_absolute_uri()
            # If the redirect url has the same scheme and net location then just
            # use the path as the "next" url.
            redirect_scheme, redirect_netloc = urlparse(resolved_redirect_url)[:2]
            current_scheme, current_netloc = urlparse(current_path_for_next)[:2]
            if (not redirect_scheme or redirect_scheme == current_scheme) and (
                not redirect_netloc or redirect_netloc == current_netloc
            ):
                current_path_for_next = request.get_full_path()
            return redirect_to_login(current_path_for_next, resolved_redirect_url, redirect_field_name)

        return _wrapped_view

    return decorator
