import pytest
from django.core.management import call_command
from dynpy.logger.models import Log
from tests.management.commands.success_logging_command import Command as SuccessLoggingCommand

pytestmark = pytest.mark.django_db


def test_that_no_log_is_saved_if_no_logging_is_true():
    call_command("success_logging_command", no_logging=True)
    assert Log.objects.all().count() == 0


def test_that_run_is_called_if_no_logging_is_true(mocker):
    mock_run = mocker.patch(
        "tests.management.commands.success_logging_command.Command.run",
        return_value=None,
    )
    call_command("success_logging_command", no_logging=True)
    mock_run.assert_called_once()


def test_that_messages_are_printed_to_the_console_if_no_logging_is_true(capfd):
    call_command("success_logging_command", no_logging=True)
    out, err = capfd.readouterr()
    assert "test log message" in out


def test_that_log_is_saved_if_no_logging_is_not_passed_to_command():
    call_command("success_logging_command")
    assert Log.objects.all().count() == 1


def test_messages_are_not_written_to_command_body_if_no_logging_is_true():
    slc = SuccessLoggingCommand()
    slc.handle(run_as="user", no_logging=True)
    assert slc.body.getvalue() == ""
