import pytest
import strawberry
from django.contrib.auth.models import Permission
from django.http import HttpRequest, HttpResponse
from graphql import ExecutionResult, GraphQLError
from strawberry.django.context import StrawberryDjangoContext

from dynpy.graphql.permission_classes import (
    HasCASPerm,
    IsAnonymous,
    IsAuthenticated,
    IsSuperuser,
    UserPermission,
)

pytestmark = pytest.mark.django_db


def get_query(permission_classes):
    @strawberry.type
    class Query:
        @strawberry.field(permission_classes=[permission_classes])
        def user(self) -> str:
            return "TestUser"

    return Query, "{ user }"


def execute_query(schema, query: str, request=None) -> ExecutionResult:
    if not request:
        request = HttpRequest()
    return schema.execute_sync(
        query, context_value=StrawberryDjangoContext(request=request, response=HttpResponse())
    )


def test_raises_IsAuthenticated_error_when_user_is_not_authenticated(mocker):
    # Arrange
    mocker.patch(
        "dynpy.graphql.permission_classes.IsAuthenticated.has_permission",
        return_value=False,
    )
    query, query_string = get_query(permission_classes=IsAuthenticated)
    schema = strawberry.Schema(query=query)

    # Act
    result = execute_query(schema, query_string)

    # Assert
    assert type(result.errors[0]) == GraphQLError
    assert result.errors[0].message == "User is not authenticated"


def test_raises_IsAnonymous_error_when_user_is_logged_in(mocker):
    # Arrange
    mocker.patch(
        "dynpy.graphql.permission_classes.IsAnonymous.has_permission",
        return_value=False,
    )
    query, query_string = get_query(permission_classes=IsAnonymous)
    schema = strawberry.Schema(query=query)

    # Act
    result = execute_query(schema, query_string)

    # Assert
    assert type(result.errors[0]) == GraphQLError
    assert result.errors[0].message == "User is logged in"


def describe_HasCASPerm():
    def False_if_user_is_missing_perm(test_user):
        # Arrange
        perm = Permission.objects.get(codename="view_user")
        test_user.user_permissions.remove(perm)
        request = HttpRequest()
        request.user = test_user
        query, query_string = get_query(permission_classes=HasCASPerm(perm.codename))
        schema = strawberry.Schema(query=query)

        # Act
        result = execute_query(schema, query_string, request)

        # Assert
        assert "do not have permission" in result.errors[0].message

    def True_if_user_has_perm(test_user):
        # Arrange
        perm = Permission.objects.get(codename="view_user")
        test_user.user_permissions.add(perm)
        request = HttpRequest()
        request.user = test_user
        query, query_string = get_query(permission_classes=HasCASPerm(perm.codename))
        schema = strawberry.Schema(query=query)

        # Act
        result = execute_query(schema, query_string, request)

        # Assert
        assert result.errors is None


def describe_UserPermission():
    def False_if_func_returns_False(test_user):
        # Arrange
        request = HttpRequest()
        request.user = test_user
        query, query_string = get_query(permission_classes=UserPermission(lambda user: False))
        schema = strawberry.Schema(query=query)

        # Act
        result = execute_query(schema, query_string, request)

        # Assert
        assert "do not have permission" in result.errors[0].message

    def True_if_func_Returns_True(test_user):
        # Arrange
        request = HttpRequest()
        request.user = test_user
        query, query_string = get_query(permission_classes=UserPermission(lambda user: True))
        schema = strawberry.Schema(query=query)

        # Act
        result = execute_query(schema, query_string, request)

        # Assert
        assert result.errors is None


def describe_IsSuperuser():
    def False_if_user_is_not_superuser(django_user_model):
        # Arrange
        user = django_user_model.objects.create(is_superuser=False)
        request = HttpRequest()
        request.user = user
        query, query_string = get_query(permission_classes=IsSuperuser)
        schema = strawberry.Schema(query=query)

        # Act
        result = execute_query(schema, query_string, request)

        # Assert
        assert "do not have permission" in result.errors[0].message

    def True_if_user_is_superuser(django_user_model):
        # Arrange
        user = django_user_model.objects.create(is_superuser=True)
        request = HttpRequest()
        request.user = user
        query, query_string = get_query(permission_classes=IsSuperuser)
        schema = strawberry.Schema(query=query)

        # Act
        result = execute_query(schema, query_string, request)

        # Assert
        assert result.errors is None
