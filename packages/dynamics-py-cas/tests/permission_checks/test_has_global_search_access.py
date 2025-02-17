from django.contrib.auth.models import Permission
from dynpy_cas.enums import Codename
from dynpy_cas.permission_checks import has_global_search_access


def test_superuser_has_permission(django_user_model):
    user = django_user_model.objects.create(is_superuser=True)
    assert has_global_search_access(user)


def test_user_with_resident_app_perm_has_permission(django_user_model):
    user = django_user_model.objects.create(is_superuser=False)
    medicaid_perm = Permission.objects.get(codename=Codename.MEDICAID_USER)
    user.user_permissions.add(medicaid_perm)

    assert has_global_search_access(user)


def test_user_without_resident_apps_does_not_have_permission(django_user_model):
    user = django_user_model.objects.create(is_superuser=False)
    billing_calendar_perm = Permission.objects.get(codename=Codename.BILLING_CALENDAR_USER)
    user.user_permissions.add(billing_calendar_perm)

    assert not has_global_search_access(user)
