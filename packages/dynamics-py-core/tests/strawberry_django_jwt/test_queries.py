from typing import List

import pytest
import strawberry
import strawberry_django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from dynpy.strawberry_django_jwt.decorators import (
    dispose_extra_kwargs,
    login_required,
    permission_required,
)
from dynpy.strawberry_django_jwt.mixins import JSONWebTokenMixin
from dynpy.strawberry_django_jwt.model_object_types import UserType
from dynpy.strawberry_django_jwt.settings import jwt_settings
from dynpy.strawberry_django_jwt.shortcuts import get_token
from graphql import get_introspection_query
from strawberry.types import Info

from tests.strawberry_django_jwt.decorators import OverrideJwtSettings
from tests.strawberry_django_jwt.strawberry_types import MyTestModel
from tests.strawberry_django_jwt.testcases import AsyncSchemaTestCase, SchemaTestCase


class QueriesTests(SchemaTestCase):
    @strawberry.type
    class Query(JSONWebTokenMixin):
        @strawberry.field
        @dispose_extra_kwargs
        def test(self, info: Info) -> UserType:
            return UserType(**info.context.user.__dict__)

    def setUp(self):
        super().setUp()

        self.other_user = get_user_model().objects.create_user("other")
        self.other_token = get_token(self.other_user)

    def test_login_required(self):
        @strawberry.type
        class Query(JSONWebTokenMixin):
            @strawberry.field
            @login_required
            def test(self) -> str:
                return "TEST"

            @strawberry.field
            @login_required
            def test_info(self, info: Info) -> str:
                return "TEST-INFO"

        self.client.schema(query=Query, mutation=self.Mutation)

        query = """
        query Test {
            test
            testInfo
        }
        """

        headers = {
            jwt_settings.JWT_AUTH_HEADER_NAME: f"{jwt_settings.JWT_AUTH_HEADER_PREFIX} {self.token}",
        }

        response = self.client.execute(query, **headers)
        data = response.data

        assert data["test"] == "TEST"
        assert response.errors is None

    @OverrideJwtSettings(JWT_ALLOW_ARGUMENT=True)
    def test_multiple_credentials(self):
        query = f"""
        query Tests($token: String!, $otherToken: String!) {{
          testBegin: test {{
            username
          }}
          testToken: test({jwt_settings.JWT_ARGUMENT_NAME}: $token) {{
            username
          }}
          testOtherToken: test({jwt_settings.JWT_ARGUMENT_NAME}: $otherToken) {{
            username
          }}
          testEnd: test {{
            username
          }}
        }}"""

        headers = {
            jwt_settings.JWT_AUTH_HEADER_NAME: f"{jwt_settings.JWT_AUTH_HEADER_PREFIX} {self.token}",
        }

        variables = {
            "token": self.token,
            "otherToken": self.other_token,
        }

        response = self.client.execute(query, variables, **headers)
        data = response.data

        assert data["testBegin"].get("username") == self.user.username
        assert data["testEnd"].get("username") == self.user.username
        assert data["testToken"].get("username") == self.user.username
        assert data["testOtherToken"].get("username") == self.other_user.username

        assert response.errors is None

    @OverrideJwtSettings(JWT_ALLOW_ARGUMENT=True)
    def test_invalid_credentials(self):
        query = f"""
        query Tests {{
          testInvalidToken: test({jwt_settings.JWT_ARGUMENT_NAME}: "invalid") {{
            username
          }}
        }}"""

        self.client.authenticate(self.token)

        response = self.client.execute(query)
        data = response.data

        assert data is None
        assert len(response.errors) == 1

    @OverrideJwtSettings(
        JWT_ALLOW_ARGUMENT=True,
        JWT_ALLOW_ANY_CLASSES=[
            "graphql.type.definition.GraphQLType",
        ],
    )
    def test_allow_any(self):
        query = f"""
        {{
          testAllowAny: test {{
            username
            id
          }}
          testInvalidToken: test({jwt_settings.JWT_ARGUMENT_NAME}: "invalid") {{
            username
            id
          }}
        }}"""

        self.client.authenticate("invalid")

        response = self.client.execute(query)

        assert response.data["testAllowAny"].get("id") is None, AnonymousUser
        assert response.data["testAllowAny"].get("username") == ""
        assert response.data["testInvalidToken"].get("id") is None, AnonymousUser
        assert response.data["testInvalidToken"].get("username") == ""

    def test_strawberry_graphql_django_fields(self):
        @strawberry.type
        class Query(JSONWebTokenMixin):
            @strawberry_django.field
            @login_required
            def test(self) -> str:
                return "TEST"

            def test2_resolver(self) -> str:
                return "TEST2"

            test2 = strawberry_django.field(login_required(test2_resolver))

            @strawberry.field
            @login_required
            def test_info(self, info: Info) -> str:
                return "TEST-INFO"

        self.client.schema(query=Query, mutation=self.Mutation)

        query = """
        query Test {
            test
            testInfo
        }
        """

        headers = {
            jwt_settings.JWT_AUTH_HEADER_NAME: f"{jwt_settings.JWT_AUTH_HEADER_PREFIX} {self.token}",
        }

        response = self.client.execute(query, **headers)
        data = response.data

        assert data["test"] == "TEST"
        assert response.errors is None

    @pytest.mark.django_db
    def test_strawberry_graphql_django_model_fields(self):
        @strawberry.type
        class Query(JSONWebTokenMixin):
            # test_model: List[MyTestModel] = strawberry_django.field()
            test_model: List[MyTestModel] = login_required(strawberry_django.field())

        self.client.schema(query=Query, mutation=self.Mutation)

        query = """
        query Test {
            testModel {
                test
            }
        }
        """

        headers = {
            jwt_settings.JWT_AUTH_HEADER_NAME: f"{jwt_settings.JWT_AUTH_HEADER_PREFIX} {self.token}",
        }

        response = self.client.execute(query, **headers)
        data = response.data

        assert data["testModel"] == []
        assert response.errors is None

    def test_permission_required(self):
        @strawberry.type
        class Query(JSONWebTokenMixin):
            @strawberry.field
            @permission_required("tests.run_tests")
            def test(self) -> str:
                return "TEST"

            @strawberry.field
            @permission_required("tests.run_tests")
            def test_info(self, info: Info) -> str:
                return "TEST"

        self.client.schema(query=Query, mutation=self.Mutation)

        query = """
        query Test {
            test
            testInfo
        }
        """

        headers = {
            jwt_settings.JWT_AUTH_HEADER_NAME: f"{jwt_settings.JWT_AUTH_HEADER_PREFIX} {self.token}",
        }

        response = self.client.execute(query, **headers)
        data = response.data

        assert data["test"] == "TEST"
        assert response.errors is None

    def test_introspection(self):
        headers = {
            jwt_settings.JWT_AUTH_HEADER_NAME: f"{jwt_settings.JWT_AUTH_HEADER_PREFIX} {self.token}",
        }

        response = self.client.execute(get_introspection_query(), **headers)

        assert response.errors is None

    def test_introspection_no_header(self):
        response = self.client.execute(get_introspection_query())

        assert response.errors is not None

    @OverrideJwtSettings(JWT_AUTHENTICATE_INTROSPECTION=False)
    def test_introspection_no_auth(self):
        headers = {
            jwt_settings.JWT_AUTH_HEADER_NAME: f"{jwt_settings.JWT_AUTH_HEADER_PREFIX} {self.token}",
        }

        response = self.client.execute(get_introspection_query(), **headers)

        assert response.errors is None

    @OverrideJwtSettings(JWT_AUTHENTICATE_INTROSPECTION=False)
    def test_introspection_no_auth_no_header(self):
        response = self.client.execute(get_introspection_query())

        assert response.errors is None


class AsyncQueriesTests(AsyncSchemaTestCase):
    @strawberry.type
    class Query(JSONWebTokenMixin):
        @strawberry.field
        @dispose_extra_kwargs
        async def test(self, info: Info) -> UserType:
            return UserType(**info.context.user.__dict__)

    def setUp(self):
        super().setUp()

        self.other_user = get_user_model().objects.create_user("other")
        self.other_token = get_token(self.other_user)

    async def test_login_required(self):
        @strawberry.type
        class Query(JSONWebTokenMixin):
            @strawberry.field
            @login_required
            async def test(self) -> str:
                return "TEST"

            @strawberry.field
            @login_required
            async def test_info(self, info: Info) -> str:
                return "TEST-INFO"

        self.client.schema(query=Query, mutation=self.Mutation)

        query = """
        query Test {
            test
            testInfo
        }
        """

        self.client.authenticate(self.token)

        response = await self.client.execute(query)
        data = response.data

        assert data["test"] == "TEST"
        assert response.errors is None

    @OverrideJwtSettings(JWT_ALLOW_ARGUMENT=True)
    async def test_multiple_credentials(self):
        query = f"""
        query Tests($token: String!, $otherToken: String!) {{
          testBegin: test {{
            username
          }}
          testToken: test({jwt_settings.JWT_ARGUMENT_NAME}: $token) {{
            username
          }}
          testOtherToken: test({jwt_settings.JWT_ARGUMENT_NAME}: $otherToken) {{
            username
          }}
          testEnd: test {{
            username
          }}
        }}"""

        self.client.authenticate(self.token)

        variables = {
            "token": self.token,
            "otherToken": self.other_token,
        }

        response = await self.client.execute(query, variables)
        data = response.data

        assert data["testBegin"].get("username") == self.user.username
        assert data["testEnd"].get("username") == self.user.username
        assert data["testToken"].get("username") == self.user.username
        assert data["testOtherToken"].get("username") == self.other_user.username

        assert response.errors is None

    @OverrideJwtSettings(JWT_ALLOW_ARGUMENT=True)
    async def test_invalid_credentials(self):
        query = f"""
        query Tests {{
          testInvalidToken: test({jwt_settings.JWT_ARGUMENT_NAME}: "invalid") {{
            username
          }}
        }}"""

        self.client.authenticate(self.token)

        response = await self.client.execute(query)
        data = response.data

        assert data is None
        assert len(response.errors) == 1

    @OverrideJwtSettings(
        JWT_ALLOW_ARGUMENT=True,
        JWT_ALLOW_ANY_CLASSES=[
            "graphql.type.definition.GraphQLType",
        ],
    )
    async def test_allow_any(self):
        query = f"""
        {{
          testAllowAny: test {{
            username
            id
          }}
          testInvalidToken: test({jwt_settings.JWT_ARGUMENT_NAME}: "invalid") {{
            username
            id
          }}
        }}"""

        self.client.authenticate("invalid")

        response = await self.client.execute(query)

        assert response.data["testAllowAny"].get("id") is None, AnonymousUser
        assert response.data["testAllowAny"].get("username") == ""
        assert response.data["testInvalidToken"].get("id") is None, AnonymousUser
        assert response.data["testInvalidToken"].get("username") == ""
