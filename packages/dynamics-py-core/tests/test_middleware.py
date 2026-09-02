from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from dynpy.middleware import HtmxLoginRequiredMiddleware, ReverseProxyHostMiddleware

pytestmark = pytest.mark.django_db()


def _make_middleware(response):
    return HtmxLoginRequiredMiddleware(Mock(return_value=response))


def test_converts_403_to_hx_redirect_for_unauthenticated_htmx(rf):
    middleware = _make_middleware(HttpResponse(status=403))
    request = rf.get("/some-page/", HTTP_HX_REQUEST="true")
    request.user = AnonymousUser()

    response = middleware(request)

    assert response.status_code == 204
    assert response["HX-Redirect"].startswith("/accounts/login/")


def test_converts_302_to_login_to_hx_redirect_for_unauthenticated_htmx(rf):
    middleware = _make_middleware(HttpResponseRedirect("/accounts/login/?next=/some-page/"))
    request = rf.get("/some-page/", HTTP_HX_REQUEST="true")
    request.user = AnonymousUser()

    response = middleware(request)

    assert response.status_code == 204
    assert response["HX-Redirect"].startswith("/accounts/login/")


def test_passes_through_200_for_unauthenticated_htmx(rf):
    ok_response = HttpResponse(b"public content")
    middleware = _make_middleware(ok_response)
    request = rf.get("/public-endpoint/", HTTP_HX_REQUEST="true")
    request.user = AnonymousUser()

    response = middleware(request)

    assert response.status_code == 200
    assert response is ok_response


def test_passes_through_302_to_non_login_url(rf):
    redirect = HttpResponseRedirect("/some-other-page/")
    middleware = _make_middleware(redirect)
    request = rf.get("/some-page/", HTTP_HX_REQUEST="true")
    request.user = AnonymousUser()

    response = middleware(request)

    assert response.status_code == 302
    assert response is redirect


def test_passes_through_authenticated_htmx_requests(rf, test_user):
    ok_response = HttpResponse(b"OK")
    middleware = _make_middleware(ok_response)
    request = rf.get("/some-page/", HTTP_HX_REQUEST="true")
    request.user = test_user

    response = middleware(request)

    assert response is ok_response


def test_passes_through_non_htmx_unauthenticated_requests(rf):
    forbidden = HttpResponse(status=403)
    middleware = _make_middleware(forbidden)
    request = rf.get("/some-page/")
    request.user = AnonymousUser()

    response = middleware(request)

    assert response.status_code == 403
    assert response is forbidden


def test_uses_hx_current_url_for_next_param(rf):
    middleware = _make_middleware(HttpResponse(status=403))
    request = rf.get(
        "/api/endpoint/",
        HTTP_HX_REQUEST="true",
        HTTP_HX_CURRENT_URL="http://testserver/dashboard/resident/123/",
    )
    request.user = AnonymousUser()

    response = middleware(request)

    qs = parse_qs(urlparse(response["HX-Redirect"]).query)
    assert qs["next"] == ["/dashboard/resident/123/"]


def test_preserves_hx_current_url_query_string(rf):
    middleware = _make_middleware(HttpResponse(status=403))
    request = rf.get(
        "/api/endpoint/",
        HTTP_HX_REQUEST="true",
        HTTP_HX_CURRENT_URL="http://testserver/dashboard/resident/123/?tab=notes",
    )
    request.user = AnonymousUser()

    response = middleware(request)

    qs = parse_qs(urlparse(response["HX-Redirect"]).query)
    assert qs["next"] == ["/dashboard/resident/123/?tab=notes"]


def test_falls_back_to_request_path_when_no_hx_current_url(rf):
    middleware = _make_middleware(HttpResponse(status=403))
    request = rf.get("/some-page/", HTTP_HX_REQUEST="true")
    request.user = AnonymousUser()

    response = middleware(request)

    qs = parse_qs(urlparse(response["HX-Redirect"]).query)
    assert qs["next"] == ["/some-page/"]


def test_merges_next_with_existing_login_url_query(rf, settings):
    settings.LOGIN_URL = "/accounts/login/?source=timeout"
    middleware = _make_middleware(HttpResponse(status=403))
    request = rf.get("/some-page/", HTTP_HX_REQUEST="true")
    request.user = AnonymousUser()

    response = middleware(request)

    qs = parse_qs(urlparse(response["HX-Redirect"]).query)
    assert qs["source"] == ["timeout"]
    assert qs["next"] == ["/some-page/"]


def test_does_not_redirect_without_hx_request_header(rf):
    forbidden = HttpResponse(status=403)
    middleware = _make_middleware(forbidden)
    request = rf.get("/some-page/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    request.user = AnonymousUser()

    response = middleware(request)

    assert response is forbidden


def _proxy_middleware(response):
    return ReverseProxyHostMiddleware(Mock(return_value=response))


EXTERNAL_HOST = "arqa-centersforspecialty.msappproxy.net"
INTERNAL_PEER = "cas.qa.centershealthcare.org"
EXTERNAL_PEER = "casqa-centersforspecialty.msappproxy.net"


def test_reports_the_external_host_for_a_proxied_request(rf, settings):
    settings.USE_X_FORWARDED_HOST = True
    settings.ALLOWED_HOSTS = [EXTERNAL_HOST]
    settings.PROXY_EXTERNAL_HOST = EXTERNAL_HOST
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")

    _proxy_middleware(HttpResponse())(request)

    assert request.get_host() == EXTERNAL_HOST


def test_leaves_the_host_alone_without_the_proxy_marker(rf, settings):
    settings.USE_X_FORWARDED_HOST = True
    settings.ALLOWED_HOSTS = ["ar.qa.centershealthcare.org", EXTERNAL_HOST]
    settings.PROXY_EXTERNAL_HOST = EXTERNAL_HOST
    request = rf.get("/", HTTP_HOST="ar.qa.centershealthcare.org")

    _proxy_middleware(HttpResponse())(request)

    assert request.get_host() == "ar.qa.centershealthcare.org"


def test_leaves_the_host_alone_when_no_external_host_is_configured(rf, settings):
    settings.USE_X_FORWARDED_HOST = True
    settings.ALLOWED_HOSTS = ["ar-web"]
    settings.PROXY_EXTERNAL_HOST = None
    request = rf.get("/", HTTP_HOST="ar-web", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")

    _proxy_middleware(HttpResponse())(request)

    assert request.get_host() == "ar-web"


def test_points_a_peer_redirect_at_the_peers_external_host(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    redirect = HttpResponseRedirect(f"https://{INTERNAL_PEER}/cas/login?service=https://ar/x")
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")

    response = _proxy_middleware(redirect)(request)

    assert response["Location"] == f"https://{EXTERNAL_PEER}/cas/login?service=https://ar/x"


def test_leaves_a_peer_redirect_alone_without_the_proxy_marker(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    location = f"https://{INTERNAL_PEER}/cas/login"
    request = rf.get("/")

    response = _proxy_middleware(HttpResponseRedirect(location))(request)

    assert response["Location"] == location


def test_leaves_redirects_to_unmapped_hosts_alone(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")

    response = _proxy_middleware(HttpResponseRedirect("/accounts/login/?next=/"))(request)

    assert response["Location"] == "/accounts/login/?next=/"


def test_honours_a_custom_marker_header(rf, settings):
    settings.USE_X_FORWARDED_HOST = True
    settings.ALLOWED_HOSTS = [EXTERNAL_HOST]
    settings.PROXY_EXTERNAL_HOST = EXTERNAL_HOST
    settings.PROXY_MARKER_HEADER = "HTTP_X_CUSTOM_PROXY"
    request = rf.get("/", HTTP_X_CUSTOM_PROXY="1")

    _proxy_middleware(HttpResponse())(request)

    assert request.get_host() == EXTERNAL_HOST


def test_points_a_peer_hx_redirect_at_the_peers_external_host(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    response = HttpResponse(status=204)
    response["HX-Redirect"] = f"https://{INTERNAL_PEER}/cas/login?next=/x"
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")

    result = _proxy_middleware(response)(request)

    assert result["HX-Redirect"] == f"https://{EXTERNAL_PEER}/cas/login?next=/x"


def test_rewrites_the_hx_redirect_the_htmx_middleware_produces(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    settings.LOGIN_URL = f"https://{INTERNAL_PEER}/cas/login"
    request = rf.get("/some-page/", HTTP_HX_REQUEST="true", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")
    request.user = AnonymousUser()
    htmx = HtmxLoginRequiredMiddleware(Mock(return_value=HttpResponse(status=403)))

    response = ReverseProxyHostMiddleware(htmx)(request)

    assert response.status_code == 204
    assert urlparse(response["HX-Redirect"]).netloc == EXTERNAL_PEER
    assert parse_qs(urlparse(response["HX-Redirect"]).query)["next"] == ["/some-page/"]


def test_external_url_swaps_a_mapped_host_for_a_proxied_request(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")

    result = ReverseProxyHostMiddleware.external_url_for_request(
        f"https://{INTERNAL_PEER}/aging/residents/", request
    )

    assert result == f"https://{EXTERNAL_PEER}/aging/residents/"


def test_external_url_upgrades_an_http_peer_to_https(rf, settings):
    """A published endpoint terminates TLS only, and internal URLs are plain
    http in some environments."""
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")

    result = ReverseProxyHostMiddleware.external_url_for_request(
        f"http://{INTERNAL_PEER}/dashboard/", request
    )

    assert result == f"https://{EXTERNAL_PEER}/dashboard/"


def test_external_url_is_unchanged_for_a_direct_request(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    internal_url = f"https://{INTERNAL_PEER}/aging/residents/"

    assert ReverseProxyHostMiddleware.external_url_for_request(internal_url, rf.get("/")) == internal_url


def test_external_url_is_unchanged_for_an_unmapped_host(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")
    other_url = "https://elsewhere.example.com/x/"

    assert ReverseProxyHostMiddleware.external_url_for_request(other_url, request) == other_url


def test_external_url_is_unchanged_without_a_request(settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    internal_url = f"https://{INTERNAL_PEER}/users/"

    assert ReverseProxyHostMiddleware.external_url_for_request(internal_url, None) == internal_url
    assert ReverseProxyHostMiddleware.external_url_for_request(internal_url, False) == internal_url


def test_remembers_a_proxied_visit_in_the_session(rf, settings):
    settings.USE_X_FORWARDED_HOST = True
    settings.ALLOWED_HOSTS = [EXTERNAL_HOST]
    settings.PROXY_EXTERNAL_HOST = EXTERNAL_HOST
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")
    request.session = {}

    _proxy_middleware(HttpResponse())(request)

    assert request.session[ReverseProxyHostMiddleware.SESSION_KEY] is True


def test_treats_a_later_markerless_request_in_the_session_as_proxied(rf, settings):
    settings.USE_X_FORWARDED_HOST = True
    settings.ALLOWED_HOSTS = [EXTERNAL_HOST]
    settings.PROXY_EXTERNAL_HOST = EXTERNAL_HOST
    request = rf.get("/partial/", HTTP_HX_REQUEST="true")
    request.session = {ReverseProxyHostMiddleware.SESSION_KEY: True}

    _proxy_middleware(HttpResponse())(request)

    assert request.get_host() == EXTERNAL_HOST


def test_does_not_remember_a_direct_visit(rf, settings):
    settings.PROXY_EXTERNAL_HOST = EXTERNAL_HOST
    request = rf.get("/", HTTP_REFERER=f"https://{EXTERNAL_HOST}/dashboard/")
    request.session = {}

    _proxy_middleware(HttpResponse())(request)

    assert request.session == {}
    assert ReverseProxyHostMiddleware.arrived_through_proxy(request) is False


def test_rewrites_a_peer_redirect_for_a_remembered_session(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    request = rf.get("/partial/", HTTP_HX_REQUEST="true")
    request.session = {ReverseProxyHostMiddleware.SESSION_KEY: True}
    redirect = HttpResponseRedirect(f"https://{INTERNAL_PEER}/cas/login")

    response = _proxy_middleware(redirect)(request)

    assert response["Location"] == f"https://{EXTERNAL_PEER}/cas/login"


def test_external_url_swaps_a_mapped_host_that_carries_a_port(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")

    result = ReverseProxyHostMiddleware.external_url_for_request(
        f"https://{INTERNAL_PEER}:8443/cas/login?next=/x", request
    )

    assert result == f"https://{EXTERNAL_PEER}/cas/login?next=/x"


def test_external_url_leaves_a_relative_location_alone(rf, settings):
    settings.PROXY_HOST_MAP = {INTERNAL_PEER: EXTERNAL_PEER}
    request = rf.get("/", HTTP_X_MS_PROXY="AzureAD-Application-Proxy")

    assert (
        ReverseProxyHostMiddleware.external_url_for_request("/accounts/login/", request)
        == "/accounts/login/"
    )
