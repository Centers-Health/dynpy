import pytest
from django.utils import timezone

from tests.models import TestTimestampedModel

pytestmark = pytest.mark.django_db


def test_that_created_at_is_set_to_now_on_creation():
    tic = timezone.now()
    ttm = TestTimestampedModel.objects.create()
    toc = timezone.now()
    assert tic < ttm.created_at < toc


def test_that_created_at_does_not_change_on_update():
    ttm = TestTimestampedModel.objects.create()
    old_created_at = ttm.created_at
    ttm.test_char_field = "test"
    ttm.save()
    assert ttm.created_at == old_created_at


def test_that_updated_at_is_set_to_now_on_creation():
    tic = timezone.now()
    ttm = TestTimestampedModel.objects.create()
    toc = timezone.now()
    assert tic < ttm.updated_at < toc


def test_that_updated_at_changes_on_update():
    ttm = TestTimestampedModel.objects.create()
    old_updated_at = ttm.updated_at
    ttm.test_char_field = "test"
    ttm.save()
    assert ttm.updated_at > old_updated_at
