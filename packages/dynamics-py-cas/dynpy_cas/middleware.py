from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, resolve_url
from django.urls import NoReverseMatch, resolve, reverse
from django.urls.exceptions import Resolver404
from django.utils.encoding import force_bytes
from dynpy.strawberry_django_jwt.utils import set_jwt_cookie

from dynpy_cas.permission_checks import has_edit_permission


class OTPRequiredMiddleware:
    """
    A middleware to redirect a user to setup an mfa device if none are enabled
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.OTP_REQUIRED:
            return self.get_response(request)

        allowed_urls = settings.OTP_ALLOWED_URLS if hasattr(settings, "OTP_ALLOWED_URLS") else []

        try:
            resolver_match = resolve(request.path)
        except Resolver404:
            return HttpResponseNotFound()

        is_allowed_url = resolver_match.view_name in allowed_urls
        user_permissions = set(request.user.user_permissions.values_list("codename", flat=True))
        has_mfa_perm = "ext_has_mfa_method" in user_permissions

        if request.user.is_authenticated and not (is_allowed_url or has_mfa_perm):
            return self._get_redirect()

        return self.get_response(request)

    def _get_redirect(self):
        try:
            return redirect("two_factor:setup")
        except NoReverseMatch:
            return redirect(settings.BASE_CAS_URL + "/mfa/account/two_factor/setup")


class JWTCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        response = self.get_response(request)
        if user.is_authenticated:
            set_jwt_cookie(user, response)
        return response


class ReadOnlyMiddleware:
    """
    A middleware to disable editing for users that do not have edit permission
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        response = self.get_response(request)

        if self.user_can_edit(request):
            return response

        if request.method != "GET":
            http_referer = request.headers.get("referer")
            if http_referer:
                messages.error(request, "You do not have editor permissions!")
                return redirect(http_referer)
            else:
                return redirect(resolve_url(settings.LOGIN_REDIRECT_URL))

        if self.is_html_response(response):
            return self.make_response_readonly(response)

        return response

    def user_can_edit(self, request):
        allowed_urls = [reverse(url) for url in getattr(settings, "READ_ONLY_ALLOWED_URLS", [])]
        app_name = resolve(request.path).app_name
        is_allowed_url = request.path in allowed_urls
        user_has_edit_permission = not app_name or has_edit_permission(request.user, app_name)
        return user_has_edit_permission or is_allowed_url

    def make_response_readonly(self, response):
        soup = BeautifulSoup(response.content, "html.parser")
        post_forms = soup.select('form[method="POST"],form[method="post"]')

        for form in post_forms:
            self.make_form_readonly(form)

        response.content = force_bytes(soup)

        return response

    def make_form_readonly(self, form):
        submit_btns = form.select('[type="submit"]')
        fields = form.select("input,select,textarea,button")
        for btn in submit_btns:
            btn.decompose()
        for field in fields:
            attrs = field.attrs or {}
            attrs["disabled"] = True
            field.attrs = attrs

    def is_html_response(self, response):
        return response.headers.get("Content-Type", "").startswith("text/html")
