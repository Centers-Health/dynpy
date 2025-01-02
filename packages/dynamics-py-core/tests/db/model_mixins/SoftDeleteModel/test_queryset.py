import pytest
from django.utils import timezone

from tests.models import TestSoftDeleteModel

pytestmark = pytest.mark.django_db


def test_that_objects_manager_only_queries_non_deleted_records():
    tsdm1 = TestSoftDeleteModel.objects.create()
    tsdm2 = TestSoftDeleteModel.objects.create(deleted_at=timezone.now())
    assert tsdm1 in TestSoftDeleteModel.objects.all()
    assert tsdm2 not in TestSoftDeleteModel.objects.all()


def test_that_all_objects_manager_includes_soft_deleted_records():
    tsdm1 = TestSoftDeleteModel.objects.create()
    tsdm2 = TestSoftDeleteModel.objects.create(deleted_at=timezone.now())
    assert tsdm1 in TestSoftDeleteModel.all_objects.all()
    assert tsdm2 in TestSoftDeleteModel.all_objects.all()
