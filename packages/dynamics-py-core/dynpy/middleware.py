from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit, urlunparse, urlunsplit

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import resolve_url


class HealthCheckMiddleware:
    """
    Returns 'OK' for requests to the health check path (default: /up/).

    Override the path with settings.HEALTH_CHECK_PATH.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.health_check_path = getattr(settings, "HEALTH_CHECK_PATH", "/up/")

    def __call__(self, request):
        is_health_check_request = request.path == self.health_check_path
        return HttpResponse("OK") if is_health_check_request else self.get_response(request)


class ReverseProxyHostMiddleware:
    """Restores the external hostname where a proxy rewrites Host without
    sending X-Forwarded-Host, and repoints cross-app redirects at the peer's
    external hostname.

    Place after SessionMiddleware, before the middleware that read the host.
    Requires settings.USE_X_FORWARDED_HOST.
    """

    DEFAULT_MARKER_HEADER = "HTTP_X_MS_PROXY"
    REDIRECT_HEADERS = ("Location", "HX-Redirect")
    SESSION_KEY = "arrived_through_proxy"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._remember_origin(request)

        external_host = self.external_host()
        if external_host and self.arrived_through_proxy(request):
            request.META["HTTP_X_FORWARDED_HOST"] = external_host

        response = self.get_response(request)

        for header in self.REDIRECT_HEADERS:
            if header in response:
                response[header] = self.external_url_for_request(response[header], request)
        return response

    @staticmethod
    def external_host():
        return getattr(settings, "PROXY_EXTERNAL_HOST", None)

    @staticmethod
    def host_map():
        return getattr(settings, "PROXY_HOST_MAP", None) or {}

    @classmethod
    def carries_marker(cls, request):
        meta = getattr(request, "META", None)
        if meta is None:
            return False
        return getattr(settings, "PROXY_MARKER_HEADER", cls.DEFAULT_MARKER_HEADER) in meta

    @classmethod
    def arrived_through_proxy(cls, request):
        if cls.carries_marker(request):
            return True

        session = getattr(request, "session", None)
        return bool(session and session.get(cls.SESSION_KEY))

    @classmethod
    def external_url_for_request(cls, url, request):
        if not url or not cls.arrived_through_proxy(request):
            return url

        parts = urlsplit(url)
        external_host = cls.host_map().get(parts.hostname)
        if not external_host:
            return url
        return urlunsplit(parts._replace(scheme="https", netloc=external_host))

    @classmethod
    def _remember_origin(cls, request):
        session = getattr(request, "session", None)
        if session is None or not cls.carries_marker(request):
            return
        if not session.get(cls.SESSION_KEY):
            session[cls.SESSION_KEY] = True


class HtmxLoginRequiredMiddleware:
    """Convert auth-failure responses into HTMX-compatible login redirects.

    When a session expires while a user has an idle tab open, subsequent HTMX
    requests hit permission checks that raise PermissionDenied (403) or follow
    redirect chains that break the HTMX swap. This middleware lets the view
    execute normally, then converts 302-to-login or 403 responses into a 204
    with an HX-Redirect header that HTMX handles natively as a full-page
    redirect. Public endpoints that return 200 are unaffected.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.headers.get("HX-Request") != "true":
            return response

        if not request.user.is_authenticated and self._is_auth_failure(response):
            login_url = resolve_url(settings.LOGIN_URL)
            next_url = self._get_next_url(request)
            redirect_url = self._build_redirect_url(login_url, next_url)

            hx_response = HttpResponse(status=204)
            hx_response["HX-Redirect"] = redirect_url
            return hx_response

        return response

    def _is_auth_failure(self, response):
        if response.status_code == 403:
            return True
        if response.status_code == 302:
            login_path = urlparse(resolve_url(settings.LOGIN_URL)).path
            location = response.get("Location", "")
            return urlparse(location).path == login_path
        return False

    def _get_next_url(self, request):
        hx_current_url = request.headers.get("HX-Current-URL", "")
        if hx_current_url:
            parsed = urlparse(hx_current_url)
            return f"{parsed.path}?{parsed.query}" if parsed.query else parsed.path
        return request.get_full_path()

    @staticmethod
    def _build_redirect_url(login_url, next_url):
        """Build login redirect URL, safely preserving any existing query params."""
        parsed = urlparse(login_url)
        query_params = parse_qsl(parsed.query, keep_blank_values=True)
        query_params.append(("next", next_url))
        return urlunparse(parsed._replace(query=urlencode(query_params)))
