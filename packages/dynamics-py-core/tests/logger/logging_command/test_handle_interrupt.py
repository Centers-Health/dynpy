import pytest
from django.core.management import call_command

from dynpy.logger.enums import LogStatus
from dynpy.logger.models import Log

pytestmark = pytest.mark.django_db


def test_that_it_sets_the_status_to_TERM():
    call_command("interrupt_logging_command")

    interrupt_log = Log.objects.first()
    assert interrupt_log.status == LogStatus.TERM


def test_that_it_prints_and_saves_a_message(capfd):
    message = "Command was terminated"
    call_command("interrupt_logging_command")

    capture = capfd.readouterr()
    assert message in capture.out

    interrupt_log = Log.objects.first()
    assert message in interrupt_log.body
