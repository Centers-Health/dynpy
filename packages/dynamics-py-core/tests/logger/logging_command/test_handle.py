import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from dynpy.logger.management.base import LoggingCommand
from dynpy.logger.models import Log
from tests.management.commands.success_logging_command import Command as SuccessLoggingCommand

pytestmark = pytest.mark.django_db


def test_that_it_calls_start(mocker):
    spy = mocker.spy(LoggingCommand, "start")
    call_command("success_logging_command")
    spy.assert_called_once()


def test_that_it_calls_run(mocker):
    spy = mocker.spy(SuccessLoggingCommand, "run")
    call_command("success_logging_command")
    spy.assert_called_once()


def test_that_it_calls_handle_error_on_error(mocker):
    spy = mocker.spy(LoggingCommand, "handle_error")
    with pytest.raises(CommandError):
        call_command("error_logging_command")
    spy.assert_called_once()


def test_that_it_calls_end_on_success(mocker):
    spy = mocker.spy(LoggingCommand, "end")
    call_command("success_logging_command")
    spy.assert_called_once()


def test_that_it_calls_end_on_error(mocker):
    spy = mocker.spy(LoggingCommand, "end")
    with pytest.raises(CommandError):
        call_command("error_logging_command")
    spy.assert_called_once()


def test_that_it_calls_end_on_interrupt(mocker):
    spy = mocker.spy(LoggingCommand, "end")
    call_command("interrupt_logging_command")
    spy.assert_called_once()


def test_it_writes_stdout_to_log_body_and_console(capfd):
    call_command("success_logging_command")
    captured = capfd.readouterr()
    assert "test log message" in Log.objects.first().body
    assert "test log message" in captured.out


def test_it_raises_key_error_with_hint_if_run_as_is_not_set():
    slc = SuccessLoggingCommand()
    with pytest.raises(KeyError) as e:
        slc.handle()
    assert "HINT" in str(e.value)


def test_self_stdout_write_is_disabled():
    slc = SuccessLoggingCommand()
    with pytest.raises(NotImplementedError):
        slc.dummy_self_stdout_write()
