from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from dynpy_cas.permission_syncer import PermissionSyncer


def test_can_accept_permission_name_changes(django_user_model):
    """
    If a permission already exists in the client project, leave Permission.name
    the way it is on the client side. We only really care about the codename,
    so if the client want to customize the name the perm syncer should not
    override that
    """
    # Arrange
    user = django_user_model.objects.create(
        username="username",
        email="email",
    )
    user_content_type = ContentType.objects.get_for_model(django_user_model)
    permission = Permission.objects.create(
        name="client name", codename="permission", content_type=user_content_type
    )
    user.user_permissions.add(permission)
    user.save()

    # Act
    perm_syncer = PermissionSyncer(user=user, permissions=["permission"])
    perm_syncer.sync()

    # Assert
    permission.refresh_from_db()
    user.refresh_from_db()
    assert permission.codename == "permission"
    assert permission.name == "client name"
    user_app_label = django_user_model._meta.app_label
    assert user.has_perm(f"{user_app_label}.permission")
