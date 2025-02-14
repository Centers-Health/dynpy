import typing
from operator import attrgetter

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from strawberry.permission import BasePermission
from strawberry.types import Info

User = get_user_model()


class HasAPIKey(BasePermission):
    message = "Not authenticated. Do you have an API Key?"

    # This method can also be async!
    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        if settings.DEBUG:
            print("GraphQL: Authentication is automatically good, since debug=True")
            return True

        # Get request
        request = info.context.request

        # Pull auth header, this checks the ar one too, since at the time of implementation that is
        # what was being used. However it also has a fallback of the one we would like to use going
        # forward. This way we don't need to upgrade immediately.
        # TODO: remove the extra ar check once the other one is implemented for mentor as well
        auth_header = request.headers.get("authorizationar") or request.headers.get("authorization")
        if not auth_header:
            return False

        if len(auth_header.split(" ")) != 2:
            return False

        prefix, api_key = auth_header.split(" ")
        return prefix.lower() == "bearer" and api_key == settings.GRAPH_API_KEY


def OrPermission(permission_classes: typing.List[BasePermission]):
    class _OrPermission(BasePermission):
        message = "You do not have permission to perform this action"

        def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
            return any(
                PermissionClass().has_permission(source, info, **kwargs)
                for PermissionClass in permission_classes
            )

    return _OrPermission


def UserPermission(perm_func: typing.Callable[[User], bool], message: typing.Optional[str] = None):
    """
    Factory for permission classes that check if the user meets certain criteria.
    """

    class _UserPermission(BasePermission):
        def __init__(self) -> None:
            super().__init__()
            self.message = message or "You do not have permission to perform this action"

        def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
            user = info.context.request.user
            return perm_func(user)

    return _UserPermission


IsAuthenticated = UserPermission(attrgetter("is_authenticated"), "User is not authenticated")
IsAnonymous = UserPermission(attrgetter("is_anonymous"), "User is logged in")
IsSuperuser = UserPermission(attrgetter("is_superuser"))


def HasCASPerm(codename: str):
    def user_has_CAS_perm(user):
        user_content_type = ContentType.objects.get_for_model(User)
        perm_str = f"{user_content_type.app_label}.{codename}"
        return user.has_perm(perm_str)

    return UserPermission(user_has_CAS_perm)
