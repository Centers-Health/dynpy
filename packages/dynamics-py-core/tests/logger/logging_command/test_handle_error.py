import pytest
from django.core import mail
from django.core.management import call_command
from django.core.management.base import CommandError
from dynpy.logger.enums import LogStatus
from dynpy.logger.models import Log, Watcher

pytestmark = pytest.mark.django_db


def test_that_it_sets_the_status_to_FAIL():
    with pytest.raises(CommandError):
        call_command("error_logging_command")

    error_log = Log.objects.first()
    assert error_log.status == LogStatus.FAIL


def test_that_it_prints_the_stacktrace(capfd):
    with pytest.raises(CommandError):
        call_command("error_logging_command")

    capture = capfd.readouterr()
    assert "Command Failed" in capture.out


def test_that_it_sends_an_email():
    Watcher.objects.create(email="watcher@email.com")
    with pytest.raises(CommandError):
        call_command("error_logging_command")
    assert len(mail.outbox) == 1


def test_that_it_sends_to_watcher():
    Watcher.objects.create(email="watcher@email.com")
    with pytest.raises(CommandError):
        call_command("error_logging_command")
    assert "watcher@email.com" in mail.outbox[0].to


def test_that_the_exception_is_in_the_email_body():
    Watcher.objects.create(email="watcher@email.com")
    with pytest.raises(CommandError) as e:  # noqa: PT011
        call_command("error_logging_command")
    assert str(e.value) in mail.outbox[0].body
