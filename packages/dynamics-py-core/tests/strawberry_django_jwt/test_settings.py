from datetime import timedelta

import pytest
from django.test import TestCase
from dynpy.strawberry_django_jwt import settings


class SettingsTests(TestCase):
    def test_perform_import(self):
        f = settings.perform_import(id, "")
        assert f == id

        f = settings.perform_import("datetime.timedelta", "")
        assert f == timedelta

    def test_import_from_string_error(self):
        with pytest.raises(ImportError):
            settings.import_from_string("import.error", "")

    def test_reload_settings(self):
        _ = settings.jwt_settings.JWT_ALGORITHM
        settings.reload_settings(setting="TEST")

        assert settings.jwt_settings._cached_attrs

        delattr(settings.jwt_settings, "_user_settings")
        settings.jwt_settings.reload()

        assert not settings.jwt_settings._cached_attrs
