import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from dynpy_cas.enums import Codename


@pytest.fixture
def test_user(django_user_model):
    user = django_user_model.objects.create(username="test_username", first_name="John", last_name="Doe")
    user.set_password("test_password")
    user.save()
    user.refresh_from_db()

    return user


@pytest.mark.django_db
@pytest.fixture(autouse=True)
def _populate_permissions(django_user_model):
    perms = list(Codename)
    content_type = ContentType.objects.get_for_model(django_user_model)
    for perm in perms:
        Permission.objects.get_or_create(
            codename=perm.value,
            content_type=content_type,
            name=perm.value,
            defaults={"codename": perm.value},
        )
