from typing import List, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class PermissionSyncer:
    """
    Class for syncing user permissions sent over from the CAS server to the user record
    on the client side

    Usage:
        PermissionSyncer(user, permissions).sync()
    """

    CAS_PERM_PREFIX = "ext_"

    def __init__(self, user: User, permissions: Optional[List[str]]) -> None:
        self.user = user
        self.permissions = permissions

    def sync(self):
        if self.permissions is None:
            return
        self._remove_old_perms()
        self._add_new_perms()

    def _remove_old_perms(self):
        self.user.user_permissions.remove(*self._get_old_perms())

    def _add_new_perms(self):
        self.user.user_permissions.add(*self._get_new_perms())

    def _get_old_perms(self):
        return Permission.objects.filter(
            user=self.user, codename__startswith=self.CAS_PERM_PREFIX
        ).exclude(codename__in=self.permissions)

    def _get_new_perms(self):
        user_content_type = ContentType.objects.get_for_model(User)
        return [self._get_or_create_perm(codename, user_content_type) for codename in self.permissions]

    def _get_or_create_perm(self, codename, content_type):
        perm, _ = Permission.objects.get_or_create(
            codename=codename, content_type=content_type, defaults={"name": codename}
        )
        return perm
