import pytest

from dynpy_gfl.paginators import InfiniteScrollPaginator


@pytest.fixture(autouse=True)
def _100_users(django_user_model):
    for i in range(100):
        django_user_model.objects.create(username=f"test_user{i}")


def describe_custom_paginator():
    def it_paginates_page_1(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = InfiniteScrollPaginator(object_list, 10, position=0)
        qs = paginator.paginated_object_list
        assert len(qs) == 10
        assert qs[0].username == "test_user0"
        assert qs[9].username == "test_user9"

    def it_paginates_page_2(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = InfiniteScrollPaginator(object_list, 10, position=10)
        qs = paginator.paginated_object_list
        assert len(qs) == 10
        assert qs[0].username == "test_user10"
        assert qs[9].username == "test_user19"

    def sets_hs_next_to_true_when_per_page_equals_object_list(django_user_model):
        """
        To avoid an extra query has_next is true when the per_page is equal to the paginated_object_list
        """
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = InfiniteScrollPaginator(object_list, 10, position=0)
        assert paginator.has_next is True

    def sets_has_next_to_false_when_the_object_list_is_less_than_the_per_page(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = InfiniteScrollPaginator(object_list, 10, position=95)
        assert paginator.has_next is False

    def does_not_error_when_top_is_bigger_than_list(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = InfiniteScrollPaginator(object_list, 10, position=95)
        qs = paginator.paginated_object_list
        assert len(qs) == 5
        assert qs[0].username == "test_user95"
        assert qs[4].username == "test_user99"
