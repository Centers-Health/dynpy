from importlib import reload

import dynpy.strawberry_django_jwt
from dynpy.strawberry_django_jwt.settings import jwt_settings
from dynpy.strawberry_django_jwt.shortcuts import get_token
from dynpy.strawberry_django_jwt.signals import token_issued, token_refreshed

from tests.strawberry_django_jwt.context_managers import (
    back_to_the_future,
    catch_signal,
    refresh_expired,
)
from tests.strawberry_django_jwt.decorators import OverrideJwtSettings


class TokenAuthMixin:
    def test_token_auth(self):
        with catch_signal(token_issued) as token_issued_handler:
            response = self.execute(
                {
                    self.user.USERNAME_FIELD: self.user.get_username(),
                    "password": "dolphins",
                }
            )

        data = response.data["tokenAuth"]

        assert token_issued_handler.call_count == 1

        assert response.errors is None
        self.assertUsernameIn(data["payload"])

    def test_token_auth_invalid_credentials(self):
        response = self.execute(
            {
                self.user.USERNAME_FIELD: self.user.get_username(),
                "password": "wrong",
            }
        )

        assert response.errors is not None


class VerifyMixin:
    def test_verify(self):
        response = self.execute(
            {
                "token": self.token,
            }
        )

        payload = response.data["verifyToken"]["payload"]

        assert response.errors is None
        self.assertUsernameIn(payload)

    def test_verify_invalid_token(self):
        response = self.execute(
            {
                "token": "invalid",
            }
        )

        assert response.errors is not None


class RefreshMixin:
    def test_refresh(self):
        with catch_signal(token_refreshed) as token_refreshed_handler, back_to_the_future(seconds=1):
            response = self.execute(
                {
                    "token": self.token,
                }
            )

        data = response.data["refreshToken"]
        token = data["token"]
        payload = data["payload"]

        assert token_refreshed_handler.call_count == 1

        assert response.errors is None
        assert token != self.token
        self.assertUsernameIn(data["payload"])
        assert payload["origIat"] == self.payload.origIat
        assert payload["exp"] > self.payload.exp

    def test_missing_token(self):
        response = self.execute({})
        assert response.errors is not None

    def test_refresh_expired(self):
        with refresh_expired():
            response = self.execute(
                {
                    "token": self.token,
                }
            )

        assert response.errors is not None

    @OverrideJwtSettings(JWT_ALLOW_REFRESH=False)
    def test_refresh_error(self):
        reload(dynpy.strawberry_django_jwt.mutations)
        token = get_token(self.user, origIat=None)
        response = self.execute(
            {
                "token": token,
            }
        )

        assert response.errors is not None


class AsyncRefreshMixin:
    async def test_refresh(self):
        with catch_signal(token_refreshed) as token_refreshed_handler, back_to_the_future(seconds=1):
            response = await self.execute(
                {
                    "token": self.token,
                }
            )

        data = response.data["refreshToken"]
        token = data["token"]
        payload = data["payload"]

        assert token_refreshed_handler.call_count == 1

        assert response.errors is None
        assert token != self.token
        self.assertUsernameIn(data["payload"])
        assert payload["origIat"] == self.payload.origIat
        assert payload["exp"] > self.payload.exp

    async def test_missing_token(self):
        response = await self.execute({})
        assert response.errors is not None

    async def test_refresh_expired(self):
        with refresh_expired():
            response = await self.execute(
                {
                    "token": self.token,
                }
            )

        assert response.errors is not None

    @OverrideJwtSettings(JWT_ALLOW_REFRESH=False)
    async def test_refresh_error(self):
        reload(dynpy.strawberry_django_jwt.mutations)
        token = get_token(self.user, origIat=None)
        response = await self.execute(
            {
                "token": token,
            }
        )

        assert response.errors is not None


class CookieTokenAuthMixin:
    def test_token_auth(self):
        response = self.execute(
            {
                self.user.USERNAME_FIELD: self.user.get_username(),
                "password": "dolphins",
            }
        )

        data = response.data["tokenAuth"]
        token = response.cookies.get(jwt_settings.JWT_COOKIE_NAME).value

        assert response.errors is None
        assert token == data["token"]
        self.assertUsernameIn(data["payload"])


class CookieRefreshMixin:
    def test_refresh(self):
        self.set_cookie()

        with back_to_the_future(seconds=1):
            response = self.execute()

        data = response.data["refreshToken"]
        token = data["token"]

        assert response.errors is None
        assert token != self.token
        self.assertUsernameIn(data["payload"])


class DeleteCookieMixin:
    def test_delete_cookie(self):
        self.set_cookie()

        response = self.execute()
        data = response.data["deleteCookie"]

        assert response.errors is None
        assert data["deleted"]
