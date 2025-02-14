from django.core.management.base import CommandParser
from dynpy.logger.enums import LogStatus
from dynpy.logger.loggers import UnexpectedErrorLogger
from dynpy.logger.management.base import ExceptionLoggingCommand


class Command(ExceptionLoggingCommand):
    service_name = "base_exception_logging_command"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        # Add arg for adding a failing error
        parser.add_argument("--has_failing_error", action="store_true")

    def run(self, *args, **options) -> str | None:
        if options.get("has_failing_error"):
            self.add_failing_error()

    def add_failing_error(self):
        self.report_error(
            UnexpectedErrorLogger, LogStatus.WARN, None, Exception("error"), is_fail_error=True
        )
