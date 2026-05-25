from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from dynpy.middleware import HtmxLoginRequiredMiddleware

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
