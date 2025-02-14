from dynpy.logger.enums import LogStatus
from dynpy.logger.management.base import LoggingCommand
from dynpy.logger.management.mixins import DWErrorLoggingCommandMixin

"""
Dummy Command used to test DWErrorLoggingCommandMixin
"""


class Command(DWErrorLoggingCommandMixin, LoggingCommand):
    class DummyException(Exception):
        def __init__(self, message) -> None:
            self.message = message
            super().__init__(message)

    service_name = "dummy_dw_error_command"

    def run(self, *args, **options):
        try:
            self.update_status(LogStatus.PASS)
            raise self.DummyException("Reporting from dummy command")
        except self.DummyException as e:
            self.report_dw_error(e, self.service_name)
