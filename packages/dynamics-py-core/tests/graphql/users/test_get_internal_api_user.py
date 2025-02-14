import pytest

from dynpy.graphql.users import INTERNAL_API_USER_USERNAME, get_internal_api_user

pytestmark = pytest.mark.django_db


def test_gets_api_user_if_exists(django_user_model):
    user = django_user_model.objects.create(username=INTERNAL_API_USER_USERNAME)
    assert get_internal_api_user() == user


def test_gets_docker_user_if_no_api_user(django_user_model):
    user = django_user_model.objects.create(username="docker")
    assert get_internal_api_user() == user


def test_raises_error_if_no_api_or_docker_user(django_user_model):
    with pytest.raises(django_user_model.DoesNotExist):
        get_internal_api_user()
