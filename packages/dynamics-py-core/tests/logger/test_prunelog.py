from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from dynpy.logger.models import Log

pytestmark = pytest.mark.django_db


def create_log(days_old: int = 10):
    log = Log.objects.create(
        app_name=__package__ or "tests",
        service_name="command name",
    )
    # Using update() to override auto_now on updated_at field
    Log.objects.filter(pk=log.pk).update(
        # Subtracting 1 to include today in count
        updated_at=timezone.now()
        - timedelta(days=days_old - 1)
    )
    return Log.objects.get(id=log.pk)


def test_that_it_deletes_old_logs():
    create_log(days_old=16)
    call_command("prunelog", "15")
    assert Log.objects.all().count() == 0


def test_that_it_does_not_delete_recent_logs():
    create_log(days_old=15)
    call_command("prunelog", "15")
    assert Log.objects.all().count() == 1


def test_that_it_defaults_to_deleting_logs_older_than_30_days():
    create_log(days_old=30)
    create_log(days_old=31)
    call_command("prunelog")
    assert Log.objects.all().count() == 1


def test_that_zero_deletes_all_logs():
    create_log(days_old=0)
    call_command("prunelog", "0")


def test_that_it_prints_the_correct_number_of_logs_deleted(capfd):
    create_log(days_old=45)
    call_command("prunelog", "30")
    out, err = capfd.readouterr()
    assert "deleted 1" in out
