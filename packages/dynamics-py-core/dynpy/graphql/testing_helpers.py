from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission
from django.http import HttpRequest, HttpResponse
from django.utils.module_loading import import_string
from strawberry.django.context import StrawberryDjangoContext

from dynpy.graphql.users import get_internal_api_user

User = get_user_model()


def gql_schema(query, variables=None, user=None):
    """
    Function used for executing graphql queries

    Requires settings.GRAPH_SCHEMA to be set to a string pointing to the project's
    graphql schema definition (`GRAPH_SCHEMA = "path.to.schema.schema"`)
    """
    try:
        schema = import_string(settings.GRAPH_SCHEMA)
    except AttributeError as e:
        raise AttributeError("settings.GRAPH_SCHEMA is not defined.") from e

    request = HttpRequest()
    request.user = user or get_internal_api_user()
    return schema.execute_sync(
        query,
        variable_values=variables,
        context_value=StrawberryDjangoContext(request=request, response=HttpResponse()),
    )


def query_requires_permission(codename, query: str, variables: Optional[dict] = None) -> bool:
    perm = Permission.objects.get(codename=codename)
    user = User.objects.create()
    user.user_permissions.remove(perm)
    result = gql_schema(query=query, variables=variables, user=user)
    return "do not have permission" in result.errors[0].message


def query_requires_superuser(query: str, variables: Optional[dict] = None) -> bool:
    user = User.objects.create(is_superuser=False)
    result = gql_schema(query=query, variables=variables, user=user)
    return "do not have permission" in result.errors[0].message


def query_requires_login(query: str, variables: Optional[dict] = None) -> bool:
    result = gql_schema(query=query, variables=variables, user=AnonymousUser())
    # Could be either message depending on whether the endpoint uses login_required decorator or
    # IsAuthenticated permission class
    error_messages = ["User is not authenticated", "do not have permission"]
    return any(message in result.errors[0].message for message in error_messages)
