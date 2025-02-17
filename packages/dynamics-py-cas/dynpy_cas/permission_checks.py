from django.contrib.contenttypes.models import ContentType

from dynpy_cas.constants import USER_ADMIN_PERMISSION, USER_EDIT_PERMISSION, USER_READ_PERMISSION
from dynpy_cas.enums import Codename


def get_app_name_for_permissions(app_name) -> str:
    # TODO: Remove if and when application is renamed to medicaid
    if app_name == "application":
        return "medicaid"
    return app_name


def has_permission(user, app_name, format_str):
    app_name = get_app_name_for_permissions(app_name)
    app_label = ContentType.objects.get_for_model(user).app_label
    return user.has_perm(format_str.format(app_label=app_label, app_name=app_name))


def has_read_permission(user, app_name):
    return has_permission(user, app_name, USER_READ_PERMISSION)


def has_edit_permission(user, app_name):
    return has_permission(user, app_name, USER_EDIT_PERMISSION)


def has_admin_permission(user, app_name):
    return has_permission(user, app_name, USER_ADMIN_PERMISSION)


def has_global_search_access(user):
    if user.is_superuser:
        return True
    RESIDENT_APP_CODENAMES = {
        Codename.AGING_USER,
        Codename.AUTHORIZATIONS_USER,
        Codename.MEDICAID_USER,
        Codename.TRACKING_USER,
        Codename.HMO_BILLING_USER,
    }
    all_perm_codenames = [perm.split(".")[1] for perm in user.get_all_permissions()]
    ext_app_user_codenames = [
        codename
        for codename in all_perm_codenames
        if codename.startswith("ext_") and codename.endswith("_user")
    ]
    return any(codename in RESIDENT_APP_CODENAMES for codename in ext_app_user_codenames)
