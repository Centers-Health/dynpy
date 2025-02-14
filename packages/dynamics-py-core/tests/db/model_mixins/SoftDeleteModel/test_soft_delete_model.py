from datetime import datetime

import pytest
from django.utils import timezone

from tests.models import TestSoftDeleteModel

pytestmark = pytest.mark.django_db


def test_that_deleted_at_defaults_to_None():
    tsdm = TestSoftDeleteModel.objects.create()
    assert tsdm.deleted_at is None


def test_that_deleted_at_can_be_set_to_datetime():
    tsdm = TestSoftDeleteModel.objects.create()
    tsdm.deleted_at = timezone.now()
    tsdm.save()
    assert isinstance(tsdm.deleted_at, datetime)


def test_that_delete_does_not_destroy_single_record():
    tsdm = TestSoftDeleteModel.objects.create()
    tsdm.delete()
    assert TestSoftDeleteModel.all_objects.all().count() == 1


def test_that_it_sets_deleted_at_to_now_on_single_record():
    tsdm = TestSoftDeleteModel.objects.create()
    tic = timezone.now()
    tsdm.delete()
    toc = timezone.now()
    assert tic < tsdm.deleted_at < toc


def test_that_it_does_not_destroy_queryset_records():
    TestSoftDeleteModel.objects.create()
    TestSoftDeleteModel.objects.create()
    TestSoftDeleteModel.objects.all().delete()
    assert TestSoftDeleteModel.all_objects.all().count() == 2


def test_that_it_sets_deleted_at_to_now_on_queryset_records():
    TestSoftDeleteModel.objects.create()
    TestSoftDeleteModel.objects.create()
    tic = timezone.now()
    TestSoftDeleteModel.objects.all().delete()
    toc = timezone.now()
    for tarm in TestSoftDeleteModel.all_objects.all():
        assert tic < tarm.deleted_at < toc


def test_that_it_returns_deleted_object_count_for_single_delete():
    tarm = TestSoftDeleteModel.objects.create()
    response = tarm.delete()
    assert response == (1, {"tests.TestSoftDeleteModel": 1})


def test_that_it_returns_deleted_object_count_for_queryset():
    TestSoftDeleteModel.objects.create()
    TestSoftDeleteModel.objects.create()
    response = TestSoftDeleteModel.objects.all().delete()
    assert response == (2, {"tests.TestSoftDeleteModel": 2})


def test_that_undelete_method_nullifies_deleted_at():
    tarm = TestSoftDeleteModel.objects.create(deleted_at=timezone.now())
    tarm.undelete()
    assert tarm.deleted_at is None


def test_that_undelete_method_throws_error_if_deleted_at_is_none():
    tarm = TestSoftDeleteModel.objects.create()
    with pytest.raises(Exception) as e:
        tarm.undelete()

    assert str(e.value) == "Cannot undelete - this record was never deleted."
