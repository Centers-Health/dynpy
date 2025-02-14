from dynpy.logger.management.base import LoggingCommand


class Command(LoggingCommand):
    service_name = "error_logging_command"

    def run(self, *args, **options) -> None:
        raise Exception("Command Failed")
