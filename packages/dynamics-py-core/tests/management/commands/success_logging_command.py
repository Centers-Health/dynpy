from django.core.management.base import CommandParser
from dynpy.logger.management.base import LoggingCommand


class Command(LoggingCommand):
    service_name = "success_logging_command"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)

    def run(self, *args, **options) -> None:
        print("test log message")

    def dummy_self_stdout_write(self):
        self.stdout.write("test self.stdout.write message")
