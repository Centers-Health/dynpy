import pytest

from dynpy.logger.enums import LogStatus
from dynpy.logger.models import Log
from tests.management.commands.success_logging_command import Command as SuccessLoggingCommand

pytestmark = pytest.mark.django_db


def test_it_prints_a_command_started_message(capfd):
    slc = SuccessLoggingCommand()
    slc.run_as = "user"
    slc.start()
    captured = capfd.readouterr()
    assert "Command Started..." in captured.out


def test_it_opens_a_new_log_with_the_correct_properties():
    slc = SuccessLoggingCommand()
    slc.run_as = "user"
    slc.start()
    assert Log.objects.last().run_as == "user"
    assert Log.objects.last().service_name == "success_logging_command"
    assert Log.objects.last().status == LogStatus.PEND
    assert Log.objects.last().app_name == "tests"


def test_the_created_log_is_saved_in_the_command_log_property():
    slc = SuccessLoggingCommand()
    slc.run_as = "user"
    slc.start()
    assert slc.log_model == Log.objects.last()
