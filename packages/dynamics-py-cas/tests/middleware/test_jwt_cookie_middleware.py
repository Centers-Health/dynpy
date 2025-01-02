from http.cookies import SimpleCookie

import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db()
User = get_user_model()


@pytest.fixture(autouse=True)
def _override_settings_for_testing_middleware(settings):
    settings.MIDDLEWARE.append("dynpy_cas.middleware.JWTCookieMiddleware")


def describe_user_signed_in():
    def adds_cookie(client):
        user = User.objects.create(username="username")
        user.set_password("password")
        user.save()
        client.login(username="username", password="password")

        response = client.get("/")
        assert "JWT" in response.cookies


def describe_user_NOT_signed_in():
    def does_not_add_cookie(client):
        client.logout()
        response = client.get("/")
        assert "JWT" not in response.cookies

    def removes_cookie(client):
        # Log out THEN add cookie. Logging out clears client cookies,
        # but we want them to stick around for the test
        client.logout()
        client.cookies = SimpleCookie({"JWT": "token"})

        response = client.get("/")

        assert "JWT" not in response.cookies
