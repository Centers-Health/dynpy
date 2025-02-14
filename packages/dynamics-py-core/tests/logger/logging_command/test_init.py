from dynpy.logger.base import BaseLogger
from dynpy.logger.enums import LogStatus
from dynpy.logger.management.base import LoggingCommand


def test_that_it_sets_properties_correctly():
    logging_command = LoggingCommand()
    assert logging_command.app_name == "dynpy.logger"
    assert logging_command.status == LogStatus.PEND
    assert isinstance(logging_command.logger, BaseLogger)
