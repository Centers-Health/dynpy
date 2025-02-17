import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage


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
    settings.GRAPH_API_KEY = "abc123"


@pytest.fixture
def test_ext_perm(django_user_model):
    content_type = ContentType.objects.get_for_model(django_user_model)
    name = "ext_perm1"
    return Permission.objects.create(
        name=name,
        content_type=content_type,
        codename=name,
    )


@pytest.fixture
def add_middleware_to_request():
    def _add_middleware_to_request(request):
        request.session = "session"
        messages = FallbackStorage(request)
        request._messages = messages

        return request

    return _add_middleware_to_request
