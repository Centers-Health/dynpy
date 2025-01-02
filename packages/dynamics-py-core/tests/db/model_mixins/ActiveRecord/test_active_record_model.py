import pytest

from dynpy.db.model_mixins import SoftDeleteModelMixin, TimestampedModelMixin
from tests.models import TestActiveRecordModel

pytestmark = pytest.mark.django_db


def test_that_it_inherits_from_soft_delete_model_mixin():
    tarm = TestActiveRecordModel.objects.create()
    assert isinstance(tarm, SoftDeleteModelMixin)


def test_that_it_inherits_from_timestamped_model_mixin():
    tarm = TestActiveRecordModel.objects.create()
    assert isinstance(tarm, TimestampedModelMixin)
