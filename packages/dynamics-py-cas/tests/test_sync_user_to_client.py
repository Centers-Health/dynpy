import pytest
from django.contrib.auth import get_user_model

from dynpy_cas.signals import sync_user_to_client

User = get_user_model()
user_app_label = User._meta.app_label

pytestmark = pytest.mark.django_db


def syncs_superuser_status():
    user = User.objects.create(is_superuser=True, is_staff=True)
    sync_user_to_client(
        sender=None,
        user=user,
        attributes={
            "ext_permissions": "[]",
            "is_superuser": False,
            "is_staff": user.is_staff,
            "email": "",
        },
    )
    user.refresh_from_db()
    assert user.is_superuser is False


def syncs_is_staff_status():
    user = User.objects.create(is_superuser=False, is_staff=True)
    sync_user_to_client(
        sender=None,
        user=user,
        attributes={
            "ext_permissions": "[]",
            "is_superuser": user.is_superuser,
            "is_staff": False,
            "email": "",
        },
    )
    user.refresh_from_db()
    assert user.is_staff is False


def syncs_user_email():
    user = User.objects.create(is_superuser=False, is_staff=True, email="one@one.com")
    updated_email = "two@two.com"
    sync_user_to_client(
        sender=None,
        user=user,
        attributes={
            "ext_permissions": "[]",
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "email": updated_email,
        },
    )
    user.refresh_from_db()
    assert user.email == updated_email
