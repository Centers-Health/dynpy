import pytest

from tests.models import TestSoftDeleteModel

pytestmark = pytest.mark.django_db


def test_that_it_removes_an_instance_from_the_database():
    tsdm = TestSoftDeleteModel.objects.create()
    tsdm.destroy()
    assert TestSoftDeleteModel.all_objects.count() == 0


def test_that_it_removes_queryset_from_the_database():
    TestSoftDeleteModel.objects.create()
    TestSoftDeleteModel.objects.create()
    TestSoftDeleteModel.objects.all().destroy()
    assert TestSoftDeleteModel.all_objects.all().count() == 0


def test_that_it_returns_destroyed_object_count_for_single_destroy():
    tarm = TestSoftDeleteModel.objects.create()
    response = tarm.destroy()
    assert response == (1, {"tests.TestSoftDeleteModel": 1})


def test_that_it_returns_destroyed_object_count_for_queryset():
    TestSoftDeleteModel.objects.create()
    TestSoftDeleteModel.objects.create()
    response = TestSoftDeleteModel.objects.all().destroy()
    assert response == (2, {"tests.TestSoftDeleteModel": 2})
