import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.http import response
from django.views.generic.edit import CreateView

from dynpy_actions.actions import ModelViewActions, ViewActions
from dynpy_actions.enums import EmbedType
from dynpy_actions.mixins import ViewActionsMixin

pytest_plugins = [
    "dynpy.pytest.fixtures",
    "dynpy_actions.fixtures",
]


@pytest.fixture(autouse=True)
def _override_settings_for_testing():
    settings.STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
    settings.SECRET_KEY = "test"
    settings.MEDIA_ROOT = "/tmp/django_test"
    settings.PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]


@pytest.fixture()
def test_user(django_user_model):
    return django_user_model.objects.create(
        username="test", password="123", first_name="John", last_name="Doe"
    )


@pytest.fixture()
def test_form():
    """
    Returns an a basic form for the User model.
    """

    class UserForm(ModelForm):
        class Meta:
            model = User
            fields = [
                "username",
                "first_name",
                "last_name",
                "is_active",
            ]

    return UserForm


@pytest.fixture()
def test_action(test_form):
    """
    Returns an action class with some basic attributes set.
    """

    class TestAction(ViewActions):
        element = test_form
        name = "test_action"
        embed_type = EmbedType.MODAL
        pre_render = True

        def handle(self, request, form, **kwargs):
            return response.HttpResponse("action handle called")

    return TestAction


@pytest.fixture()
def test_model_action(test_form):
    """
    Returns a model action class with some basic attributes set.
    """

    class TestAction(ModelViewActions):
        element = test_form
        name = "test_model_action"
        embed_type = EmbedType.MODAL
        pre_render = True

        def handle(self, request, form, **kwargs):
            return response.HttpResponse("model action handle called")

    return TestAction


@pytest.fixture()
def test_action_with_scripts(test_form):
    """
    Returns an action class with some basic attributes set.
    """

    class TestAction(ViewActions):
        element = test_form
        name = "test_action_with_scripts"
        embed_type = EmbedType.MODAL
        scripts = ["foo", "script.js"]

        def handle(self, request, form, **kwargs):
            return response.HttpResponse("action handle called")

    return TestAction


@pytest.fixture()
def test_view_with_actions(
    test_action, test_form, test_model_action, test_action_with_scripts
):
    """
    Returns a View that has actions. Simple createView
    that has a template,form and actions.
    """

    class SomeGenericView(ViewActionsMixin, CreateView):
        actions = [test_action, test_model_action, test_action_with_scripts]
        template_name = "dynpy_actions/action_generic_base_form.html"
        form_class = test_form

    return SomeGenericView
