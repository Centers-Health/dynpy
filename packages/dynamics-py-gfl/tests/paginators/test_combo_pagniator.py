import pytest
from dynpy_gfl.paginators import ComboPaginator


@pytest.fixture(autouse=True)
def _100_users(django_user_model):
    for i in range(100):
        django_user_model.objects.create(username=f"test_user{i}")


def describe_combo_paginator():
    def it_limits_results_to_per_combo_page_boundary(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = ComboPaginator(object_list, 10, position=10, per_combo_page=15, combo_page=1)
        qs = paginator.paginated_object_list
        assert len(qs) == 5
        assert qs[0].username == "test_user10"
        assert list(qs)[-1].username == "test_user14"

    def it_returns_first_10_items_on_page_1(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = ComboPaginator(object_list, 10, position=0, per_combo_page=100, combo_page=1)
        qs = paginator.paginated_object_list
        assert len(qs) == 10
        assert qs[0].username == "test_user0"
        assert list(qs)[-1].username == "test_user9"

    def it_returns_next_10_items_on_combo_page_1_position_10(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = ComboPaginator(object_list, 10, position=10, per_combo_page=100, combo_page=1)
        qs = paginator.paginated_object_list
        assert qs[0].username == "test_user10"
        assert list(qs)[-1].username == "test_user19"

    def it_returns_correct_has_next(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = ComboPaginator(object_list, 10, position=89, per_combo_page=100, combo_page=1)
        assert paginator.has_next is True

        # Does not have next because hitting the end of the combo page
        paginator = ComboPaginator(object_list, 10, position=90, per_combo_page=100, combo_page=1)
        assert paginator.has_next is False

        # Does not have next because hitting the end of the object list
        paginator = ComboPaginator(object_list, 10, position=95, per_combo_page=1000, combo_page=1)
        assert paginator.has_next is False

    def it_returns_correct_has_next_combo_page(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = ComboPaginator(object_list, 10, position=10, per_combo_page=20, combo_page=1)
        assert paginator.has_next_combo_page is True
        paginator = ComboPaginator(object_list, 10, position=10, per_combo_page=100, combo_page=1)
        assert paginator.has_next_combo_page is False

    def it_calculates_showing_start_correctly(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = ComboPaginator(object_list, 10, position=10, per_combo_page=100, combo_page=1)
        assert paginator.showing_start == 1
        paginator = ComboPaginator(object_list, 10, position=0, per_combo_page=50, combo_page=2)
        assert paginator.showing_start == 51

    def it_calculates_showing_end_correctly(django_user_model):
        object_list = django_user_model.objects.all().order_by("pk")
        paginator = ComboPaginator(object_list, 10, position=0, per_combo_page=50, combo_page=1)
        assert paginator.showing_end == 50
        paginator = ComboPaginator(object_list, 10, position=0, per_combo_page=50, combo_page=2)
        assert paginator.showing_end == 100

        # End = 100 because only 100 items in the list
        paginator = ComboPaginator(object_list, 10, position=0, per_combo_page=200, combo_page=1)
        assert paginator.showing_end == 100
