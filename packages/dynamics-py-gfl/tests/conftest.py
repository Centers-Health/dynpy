import pytest
from django.forms.models import ModelForm


@pytest.fixture
def test_user(django_user_model):
    return django_user_model.objects.create(
        username="test", password="123", first_name="John", last_name="Doe"
    )


@pytest.fixture
def test_form(django_user_model):
    """
    Returns an a basic form for the User model.
    """

    class UserForm(ModelForm):
        class Meta:
            model = django_user_model
            fields = [
                "username",
                "first_name",
                "last_name",
                "is_active",
            ]

    return UserForm
