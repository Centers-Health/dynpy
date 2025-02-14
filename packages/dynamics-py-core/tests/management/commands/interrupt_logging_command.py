from dynpy.logger.management.base import LoggingCommand


class Command(LoggingCommand):
    service_name = "interrupt_logging_command"

    def run(self, *args, **options) -> None:
        raise KeyboardInterrupt
