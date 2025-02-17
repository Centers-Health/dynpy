from django.contrib.admin import site
from dynpy.strawberry_django_jwt.refresh_token import admin
from dynpy.strawberry_django_jwt.refresh_token.utils import get_refresh_token_model
from dynpy.strawberry_django_jwt.shortcuts import create_refresh_token

from tests.strawberry_django_jwt.testcases import TestCase


class AdminTestCase(TestCase):
    def setUp(self):
        super().setUp()
        refresh_token_model = get_refresh_token_model()
        self.refresh_token = create_refresh_token(self.user)
        self.refresh_token_admin = admin.RefreshTokenAdmin(refresh_token_model, site)


class AdminTests(AdminTestCase):
    def test_revoke(self):
        request = self.request_factory.get("/")
        qs = self.refresh_token_admin.get_queryset(request)

        self.refresh_token_admin.revoke(request, qs)
        self.refresh_token.refresh_from_db()

        assert self.refresh_token.revoked is not None

    def test_is_expired(self):
        is_expired = self.refresh_token_admin.is_expired(self.refresh_token)

        assert not is_expired


class FiltersTests(AdminTestCase):
    def filter_queryset(self, **kwargs):
        request = self.request_factory.get("/", kwargs)
        request.user = self.user
        changelist = self.refresh_token_admin.get_changelist_instance(request)
        return changelist.get_queryset(request)

    def test_revoked(self):
        qs = self.filter_queryset(revoked="yes")
        assert not qs

    def test_not_revoked(self):
        qs = self.filter_queryset(revoked="no")
        assert qs

    def test_expired(self):
        qs = self.filter_queryset(expired="yes")
        assert not qs

    def test_not_expired(self):
        qs = self.filter_queryset(expired="no")
        assert qs
