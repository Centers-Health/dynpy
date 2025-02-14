import json

import pytest
from django.urls import reverse

from dynpy.erroneous.ajax_views import JSErrorView
from dynpy.erroneous.models import Error

pytestmark = pytest.mark.django_db


def test_creates_erroneous_error(rf, test_user):
    # Arrange
    post_data = {
        "colno": 1,
        "lineno": 2,
        "message": "Uncaught Error: This is a dummy js error",
        "source": "https://dynamics.localhost/dummy-path/",
        "stacktrace": "Error: This is a dummy js error",
        "window_location_href": "This is dummy window.location data",
        "device_width": "100",
        "device_height": "200",
    }
    request = rf.post(
        reverse("log_js_error"),
        data=json.dumps(post_data),
        content_type="application/json",
    )
    request.user = test_user

    # Act
    JSErrorView.as_view()(request)

    # Assert
    assert Error.objects.count() == 1


def test_info_is_put_into_error_html(rf, test_user, admin_client):
    # Arrange
    colno = 1
    lineno = 2
    message = "Uncaught Error= This is a dummy js error"
    source = "https://dynamics.localhost/dummy-path/"
    stacktrace = "Error: This is a dummy js error"
    window_location_href = "This is dummy window.location data"
    device_width = "100"
    device_height = "200"
    user_agent = "dummy user agent"

    post_data = {
        "colno": colno,
        "lineno": lineno,
        "message": message,
        "source": source,
        "stacktrace": stacktrace,
        "window_location_href": window_location_href,
        "device_width": device_width,
        "device_height": device_height,
    }
    request = rf.post(
        reverse("log_js_error"),
        data=json.dumps(post_data),
        content_type="application/json",
        HTTP_USER_AGENT=user_agent,
    )
    request.user = test_user

    # Act
    JSErrorView.as_view()(request)
    error = Error.objects.first()

    # Assert
    assert user_agent in error.html
    assert window_location_href in error.html
    assert device_width in error.html
    assert device_height in error.html
    assert message in error.html
    assert test_user.get_username() in error.html
    assert test_user.get_username() in error.html


def test_calls_log_erroneous_error(rf, mocker, test_user):
    # Arrange
    mocked_log_erroneous_error = mocker.patch(
        "dynpy.erroneous.ajax_views.log_erroneous_error", return_value=None
    )

    post_data = {
        "colno": 1,
        "lineno": 2,
        "message": "Uncaught Error: This is a dummy js error",
        "source": "https://dynamics.localhost/dummy-path/",
        "stacktrace": "Error: This is a dummy js error",
        "window_location_href": "This is dummy href data",
        "device_width": "100",
        "device_height": "200",
    }
    request = rf.post(
        reverse("log_js_error"),
        data=json.dumps(post_data),
        content_type="application/json",
    )
    request.user = test_user

    # Act
    JSErrorView.as_view()(request)

    # Assert
    mocked_log_erroneous_error.assert_called_once()
