from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import MultiValueDict
from django_filters.filters import ModelChoiceFilter
from dynpy_gfl.dataclasses import FilterByField
from dynpy_gfl.filters import FilteredModelChoiceFilter
from dynpy_gfl.filtersets import GenericFilterSet

# Helpers


def user_filterset_factory(user_model, user_filter_by_fields, default_empty=False):
    class TestFilterset(GenericFilterSet):
        users = FilteredModelChoiceFilter(
            queryset=user_model.objects.all(),
            filter_by_fields=user_filter_by_fields,
            default_empty=default_empty,
        )
        permissions = ModelChoiceFilter(queryset=Permission.objects.all(), field_name="user_permissions")

        class Meta:
            fields = ["username"]
            model = user_model

    return TestFilterset


def set_up_users_with_permissions(django_user_model):
    content_type = ContentType.objects.get_for_model(django_user_model)
    perm = Permission.objects.create(name="test_perm", content_type=content_type, codename="test_perm")

    user_with_permission = django_user_model.objects.create(username="Bob")
    user_with_permission.user_permissions.add(perm)

    user_without_permission = django_user_model.objects.create(username="John")

    return user_with_permission, user_without_permission, perm


# Tests


def test_choices_are_filtered_out(django_user_model):
    TestFilterset = user_filterset_factory(
        django_user_model,
        [FilterByField(filter_name="permissions", field_name="user_permissions", lookup_expr="")],
    )

    user_with_permission, user_without_permission, perm = set_up_users_with_permissions(
        django_user_model
    )

    filterset = TestFilterset(MultiValueDict({"permissions": [perm.pk]}))

    # Need to do this so it evaluates the filters
    filterset.qs  # noqa: B018

    assert user_with_permission in filterset.filters.get("users").extra["queryset"]
    assert user_without_permission not in filterset.filters.get("users").extra["queryset"]


def test_uses_filter_method_function_when_provided(django_user_model):
    TestFilterset = user_filterset_factory(
        django_user_model,
        [
            FilterByField(
                filter_name="permissions",
                filter_method=lambda queryset, name, value: queryset.filter(user_permissions=value),
            )
        ],
    )

    user_with_permission, user_without_permission, perm = set_up_users_with_permissions(
        django_user_model
    )

    filterset = TestFilterset(MultiValueDict({"permissions": [perm.pk]}))

    # Need to do this so it evaluates the filters
    filterset.qs  # noqa: B018

    assert user_with_permission in filterset.filters.get("users").extra["queryset"]
    assert user_without_permission not in filterset.filters.get("users").extra["queryset"]


def test_default_empty_returns_empty_queryset_by_default(django_user_model):
    TestFilterset = user_filterset_factory(
        django_user_model,
        [FilterByField(filter_name="permissions", field_name="user_permissions", lookup_expr="")],
        default_empty=True,
    )

    set_up_users_with_permissions(django_user_model)

    filterset = TestFilterset()

    # Need to do this so it evaluates the filters
    filterset.qs  # noqa: B018

    assert filterset.filters.get("users").extra["queryset"].count() == 0
