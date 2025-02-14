import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from dynpy.logger.enums import LogStatus
from dynpy.logger.loggers import DWErrorLogger
from dynpy.logger.management.base import ExceptionLoggingCommand
from dynpy.logger.models import Log


def test_add_error_adds_the_error_to_the_dict_when_not_present_in_dict():
    logging_command = ExceptionLoggingCommand()
    logging_command.add_error("error")
    assert logging_command.errors_count["error"] == 1


def test_add_error_increments_count():
    logging_command = ExceptionLoggingCommand()
    logging_command.add_error("error")
    logging_command.add_error("error")
    assert logging_command.errors_count["error"] == 2


def test_print_end_message_includes_errors_count(capsys):
    logging_command = ExceptionLoggingCommand()
    logging_command.add_error("error")
    logging_command.print_end_message()
    end_message = capsys.readouterr()
    assert "error : 1" in end_message.out


@pytest.mark.django_db()
def describe_report_error():
    def uses_logger_passed_in_to_log_the_error():
        logging_command = ExceptionLoggingCommand()
        logger = DWErrorLogger
        logging_command.report_error(logger, LogStatus.WARN, None, Exception("error"))
        error_log_entry = Log.objects.first()
        assert error_log_entry.service_name == "dw_error"

    def sets_running_commands_status_to_status_passed_in():
        logging_command = ExceptionLoggingCommand()
        logger = DWErrorLogger
        logging_command.report_error(logger, LogStatus.WARN, None, Exception("error"))
        assert logging_command.status == LogStatus.WARN

    def increments_errors_count():
        logging_command = ExceptionLoggingCommand()
        logger = DWErrorLogger
        logging_command.report_error(logger, LogStatus.WARN, None, Exception("error"))
        assert logging_command.errors_count["Exception"] == 1

    def prints_error_message(capsys):
        logging_command = ExceptionLoggingCommand()
        logger = DWErrorLogger
        logging_command.report_error(logger, LogStatus.WARN, {"test_row": "test"}, Exception("error"))
        error_message = capsys.readouterr()
        assert "Error Exception was raised by {'test_row': 'test'} -> error" in error_message.out

    def increments_fail_errors_count_if_is_fail_error_is_true():
        logging_command = ExceptionLoggingCommand()
        logger = DWErrorLogger
        logging_command.report_error(
            logger, LogStatus.WARN, None, Exception("error"), is_fail_error=True
        )
        assert logging_command.fail_errors_count == 1


@pytest.mark.django_db()
def test_command_fails_and_exits_if_fail_errors_count_exceeds_FAIL_TOLERANCE(mocker):
    mocker.patch("dynpy.logger.management.base.ExceptionLoggingCommand.FAIL_TOLERANCE", 1)
    with pytest.raises(CommandError):
        call_command("base_exception_logging_command", fail_tolerance=1, has_failing_error=True)
    assert Log.objects.last().status == LogStatus.FAIL


@pytest.mark.django_db()
def test_can_set_FAIL_TOLERANCE_via_argument():
    """
    Default is 100 and setting to 1 via argument should cause the command to fail
    """
    with pytest.raises(CommandError):
        call_command("base_exception_logging_command", fail_tolerance=1, has_failing_error=True)
    assert Log.objects.last().status == LogStatus.FAIL


def test_cannot_set_fail_errors_count_directly():
    logging_command = ExceptionLoggingCommand()
    with pytest.raises(AttributeError):
        logging_command.fail_errors_count = 1
