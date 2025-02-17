from unittest.mock import Mock

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from dynpy_cas.enums import Codename
from dynpy_cas.middleware import OTPRequiredMiddleware

pytestmark = pytest.mark.django_db()


@pytest.fixture(autouse=True)
def _override_settings_for_testing_middleware(settings):
    settings.OTP_REQUIRED = True
    settings.OTP_ALLOWED_URLS = ["mfa_login"]
    settings.BASE_CAS_URL = "http://cas.localhost"


def describe_middleware_behavior():
    def it_redirects_if_no_mfa_methods_and_isnt_allowed_url(rf, test_user):
        request = rf.get("/")
        request.user = test_user
        response = OTPRequiredMiddleware(get_response=None)(request)

        assert response.status_code == 302
        assert "two_factor/setup" in response.url

    def it_doesnt_redirect_if_mfa_methods_and_is_not_allowed_url(rf, test_user):
        request = rf.get("/")
        mfa_perm = Permission.objects.get(codename=Codename.HAS_MFA_METHOD)
        test_user.user_permissions.add(mfa_perm)
        request.user = test_user

        # The mocker return value is set to success so that if the middleware
        # does not redirect the request we know its an allowed request
        get_response_mock = Mock(return_value="success")
        response = OTPRequiredMiddleware(get_response=get_response_mock)(request)

        assert response == "success"

    def it_returns_404_if_invalid_url(rf):
        request = rf.get("/not_a_real_url")

        response = OTPRequiredMiddleware(get_response=None)(request)

        assert response.status_code == 404
