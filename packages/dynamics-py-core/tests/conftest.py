import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

pytest_plugins = "dynpy.pytest.fixtures"


@pytest.fixture(autouse=True)
def _override_settings_for_testing(settings):
    settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    settings.TESTING = True
    settings.DEBUG = False
    settings.MEDIA_ROOT = "/tmp/django_test"
    settings.PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
    settings.GRAPH_URL = "https://graph.localhost"


@pytest.fixture()
def test_user(django_user_model):
    return django_user_model.objects.create(
        username="test", password="123", first_name="John", last_name="Doe"
    )


@pytest.fixture()
def test_file():
    return SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
