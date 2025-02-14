import pytest

from dynpy.logger.enums import LogStatus
from tests.management.commands.success_logging_command import Command as SuccessLoggingCommand


def test_it_does_not_accept_invalid_statuses():
    slc = SuccessLoggingCommand()
    with pytest.raises(ValueError):
        slc.update_status("invalid")


@pytest.mark.parametrize(
    "low_status,high_status",
    [
        (LogStatus.PEND, LogStatus.PASS),
        (LogStatus.PASS, LogStatus.INFO),
        (LogStatus.INFO, LogStatus.WARN),
        (LogStatus.WARN, LogStatus.FAIL),
    ],
)
def test_it_sets_the_status_to_higher_ranked_status(low_status, high_status):
    slc = SuccessLoggingCommand()
    slc.update_status(low_status)
    slc.update_status(high_status)
    assert slc.status == high_status


@pytest.mark.parametrize(
    "low_status,high_status",
    [
        (LogStatus.PEND, LogStatus.PASS),
        (LogStatus.PASS, LogStatus.INFO),
        (LogStatus.INFO, LogStatus.WARN),
        (LogStatus.WARN, LogStatus.FAIL),
    ],
)
def test_it_does_not_set_status_to_lower_ranked_status(low_status, high_status):
    slc = SuccessLoggingCommand()
    slc.update_status(high_status)
    slc.update_status(low_status)
    assert slc.status == high_status
