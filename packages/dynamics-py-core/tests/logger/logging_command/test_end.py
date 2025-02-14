from datetime import datetime

import pytest

from dynpy.logger.enums import LogStatus
from dynpy.logger.management.base import LoggingCommand
from dynpy.logger.models import Watcher
from tests.management.commands.success_logging_command import Command as SuccessLoggingCommand

pytestmark = pytest.mark.django_db


def run_warning_logging_command():
    command = LoggingCommand()
    command.service_name = "test"
    command.run_as = "user"
    command.start()
    command.body.write("log body")
    command.update_status(LogStatus.WARN)
    command.end()


def test_that_it_sets_the_status_to_PASS_by_default():
    slc = SuccessLoggingCommand()
    slc.run_as = "user"
    slc.start()
    slc.end()
    assert slc.status == LogStatus.PASS


def test_that_it_does_not_change_the_status_if_it_has_already_been_changed_from_PEND():
    slc = SuccessLoggingCommand()
    slc.run_as = "user"
    slc.start()
    slc.status = LogStatus.WARN
    slc.end()
    assert slc.status == LogStatus.WARN


def test_that_it_prints_a_completed_message(capfd):
    slc = SuccessLoggingCommand()
    slc.run_as = "user"
    slc.start()
    slc.end()
    capture = capfd.readouterr()
    assert "Command Completed!" in capture.out


def test_that_it_updates_the_log_with_the_correct_values():
    slc = SuccessLoggingCommand()
    slc.run_as = "user"
    slc.start()
    slc.status = LogStatus.PASS
    slc.body.write("log body")
    slc.end()
    assert slc.log_model.status == LogStatus.PASS
    assert "log body" in slc.log_model.body
    assert isinstance(slc.log_model.completed_at, datetime)


def describe_status_is_warn():
    def it_sends_an_email(mailoutbox):
        Watcher.objects.create(email="watcher@email.com")
        run_warning_logging_command()
        assert len(mailoutbox) == 1

    def it_sends_to_watcher(mailoutbox):
        Watcher.objects.create(email="watcher@email.com")
        run_warning_logging_command()
        assert "watcher@email.com" in mailoutbox[0].to

    def it_sends_the_output_in_the_email(mailoutbox):
        Watcher.objects.create(email="watcher@email.com")
        run_warning_logging_command()
        assert "log body" in str(mailoutbox[0].body)
