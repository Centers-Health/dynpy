import contextlib
import io
import traceback
from collections import defaultdict
from typing import Any, Optional

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError, CommandParser

from dynpy.logger.base import BaseErrorLogger, BaseLogger
from dynpy.logger.enums import LogStatus
from dynpy.logger.models import Log, Watcher
from dynpy.logger.module import get_app_name_from_module
from dynpy.logger.stdout import tee_stdout


class LoggingCommand(BaseCommand):
    """
    To be used instead of BaseCommand to log additional information to the
    service monitor

    How to use:

    - Instead of inheriting from BaseCommand, inherit from LoggingCommand
    - Add a service_name property to the command. This will be used to label the logs.
    - Rename the comand's `handle()` method to `run()`
    - To ensure the default arguments get set, add the following line at the end of your command's `add_arguments()` method:

        ```
         return super().add_arguments(parser)
        ```

    - To log messages in the command, use the regular `print()` method. The message will print both to
        the console and to the log body
    - Use the `update_status()` method to update the command's status
    """

    app_name: str | None = None
    body: io.StringIO = io.StringIO()
    logger: BaseLogger
    service_name: Optional[str] = None
    log_model: Log
    status: str

    def __init__(self):
        super().__init__()
        self.status = LogStatus.PEND
        self.app_name = self.app_name or get_app_name_from_module(self.__module__)
        self.logger = BaseLogger(app_name=self.app_name)
        self.is_logging = True
        self.body = io.StringIO()
        self.stdout.write = self.self_stdout_write

    def self_stdout_write(self, message: str):
        """
        Disable self.stdout.write() to force usage of either print() or sys.stdout.write() to print
        messages. As of now, the method we are using to print messages to both the console and the log
        body only works with print() or sys.stdout.write(), not self.stdout.write()
        """
        raise NotImplementedError(
            "self.stdout.write is disabled in subclasses of LoggingCommand. To print messages use print() or sys.stdout.write()"
        )

    def get_service_name(self):
        """
        Gets the command's service_name, raises error if not implemented
        """
        if self.service_name is None:
            raise NotImplementedError(
                "subclasses of LoggingCommand must have a non-null service_name property."
            )
        return self.service_name

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--run-as",
            type=str,
            nargs="?",
            default="",
            help="Indicates the role of the user running the command",
        )

        parser.add_argument(
            "--no-logging",
            action="store_true",
            default=False,
            help="Run command without logging",
        )

    def run(self, *args, **kwargs) -> Optional[str]:
        """
        **This method should be implemented instead of `handle()`**
        """
        raise NotImplementedError('subclasses of LoggingCommand must implement the "run" method.')

    def handle(self, *args, **options) -> None:
        """
        `run()` method should be implemented which behaves the same way as
        the normal handle command but it is wrapped with the logger features.
        """
        if "run_as" not in options:
            raise KeyError(
                "No run-as argument was passed to the handle() method. HINT: Make sure your command's add_arguments() method returns `super().add_arguments(parser)` so the default arguments get set."
            )
        self.run_as = options["run_as"]
        if "no_logging" in options:
            self.is_logging = not options["no_logging"]
        with (
            tee_stdout(new_target=self.body, is_timestamped=True)
            if self.is_logging
            else contextlib.suppress()
        ):
            self.start()
            try:
                self.run(*args, **options)
            except KeyboardInterrupt:
                self.handle_interrupt()
            except Exception as e:
                self.handle_error()
                raise e
            finally:
                self.end()

    def start(self):
        """
        Starts the logging process as follows:

        - Prints an initial "Command Started..." message to the console
        - Creates a new log instance in the database, to be updated when command is completed
        - Stores the new log instance in the command's log_model property

        If the no_logging argument was used, no log instance in created in the database, but the message
        is still printed to the console.
        """
        print("Command Started...")
        if self.is_logging:
            self.log_model = self.logger.open_new_log(
                run_as=self.run_as,
                service_name=self.get_service_name(),
                body=str(self.body.getvalue()),
            )

    def end(self) -> None:
        """
        Ends the logging process as follows:

        - Prints a "Command Completed!" message to the console
        - Sets the log_model status and body to the command's current status and body
        - Sets the log_model completed_at field to the current datetime to mark it as complete

        If the no_logging argument was used, the log is not saved to the database, but the message is
        still printed to the console.
        """

        if self.status == LogStatus.PEND:
            self.status = LogStatus.PASS
        self.print_end_message()
        if self.is_logging:
            self.log()
        if self.status == LogStatus.WARN:
            self.send_logger_watchers_email(f"Job Finished with Status of WARN: {self.service_name}")

    def log(self):
        self.log_model.update(
            body=str(self.body.getvalue()),
            status=self.status,
            is_completed=True,
        )

    def print_end_message(self):
        """
        Prints out a message at the end of the command
        """
        print("Command Completed!")

    def update_status(self, status: str):
        """
        Update the command status to a new `LogStatus`. If the inputted status is of lower priority than the command's
        current status (as defined in this method), the command will retain its current status
        """
        if status not in LogStatus._value2member_map_:
            raise ValueError("status must be a valid LogStatus")
        status_ranks = {
            LogStatus.PEND: 0,
            LogStatus.PASS: 1,
            LogStatus.INFO: 2,
            LogStatus.WARN: 3,
            LogStatus.FAIL: 4,
            LogStatus.TERM: 5,
        }
        if status_ranks[status] > status_ranks[self.status]:
            self.status = status

    def handle_error(self) -> None:
        """
        Handles error logging as follows:

        - Sets the log status to FAIL
        - Prints the stacktrace to the console
        - Saves the stacktrace in the command's body property
        """
        self.update_status(LogStatus.FAIL)
        print(traceback.format_exc())

        self.send_logger_watchers_email(f"Failed Job: {self.service_name}")

    def send_logger_watchers_email(self, subject: str):
        to_addresses = [watcher.email for watcher in Watcher.objects.all()]
        if not to_addresses:
            return

        email_body = f"...{str(self.body.getvalue())[-1000:]}"
        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_addresses,
        )
        email.send()

    def handle_interrupt(self) -> None:
        """
        Handles interrupt as follows:

        - Sets the log status to TERM
        - Prints an interrupt message
        """
        self.update_status(LogStatus.TERM)
        print("KeyboardInterrupt: Command was terminated")


class ExceptionLoggingCommand(LoggingCommand):
    """
    Logger that also handles exceptions that are caught in the command.

    - Prints out summary of errors at the end of the command and provides
    methods to help keep track of errors count.
    - Provides a method to report errors and log them using the logger passed
      in.
    - Provides exit-early option if the fail_errors_count exceeds the FAIL_TOLERANCE.
      fail_errors_count needs to be updated in child commands via report_error when the error is the
      type that if there are too many, the command should fail (i.e. an unexpected error).

      The FAIL_TOLERANCE can be set via the command line argument --fail-tolerance
    """

    errors_count: dict
    FAIL_TOLERANCE: int = 100  # Number of errors that the command will fail at
    _fail_errors_count: int = 0  # Incremented each time an error, that contributes to Failure is added

    @property
    def fail_errors_count(self):
        return self._fail_errors_count

    @fail_errors_count.setter
    def fail_errors_count(self, new_value):
        raise AttributeError(
            "fail_errors_count should not be set directly. Use the report_error method instead."
        )

    def __init__(self):
        super().__init__()
        self.errors_count = defaultdict(int)

    def handle(self, *args, **options) -> None:
        self.FAIL_TOLERANCE = options.get("fail_tolerance") or self.FAIL_TOLERANCE
        super().handle(*args, **options)

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--fail-tolerance",
            type=int,
            default=100,
            dest="fail_tolerance",
            help="Number of fail-errors allowed before exiting the command",
        )
        super().add_arguments(parser)

    def print_end_message(self):
        super().print_end_message()
        self.print_errors_count()

    def add_error(self, error_type: str) -> None:
        """
        Adds an error to the command's errors count
        """
        self.errors_count[error_type] += 1

    def print_errors_count(self) -> None:
        """
        Prints the command's errors count to the console as a summary
        """
        for error_type, count in self.errors_count.items():
            print(f"{error_type} : {count}")

    def report_error(
        self,
        logger: BaseErrorLogger,
        status: LogStatus,
        row: Any,
        exception: Exception,
        is_fail_error: bool = False,
    ):
        """
        Uses the logger passed in to log an error and print out the error message.
        Sets the command's status to the status passed in.

        A BaseErrorLogger needs to be defined and passed in as the ErrorLogger to use
        to log the error.
        """

        exception_message = exception.message if hasattr(exception, "message") else str(exception)
        print(
            self.style.ERROR(
                f"Error {exception.__class__.__name__} was raised by {row} -> {exception_message}"
            )
        )
        logger(row, exception, self.service_name).log_action()
        self.add_error(type(exception).__name__)
        self.update_status(status)
        self._process_fail_errors(is_fail_error)

        self._check_fail_count()

    def _process_fail_errors(self, is_fail_error):
        if is_fail_error:
            self._fail_errors_count += 1

    def _check_fail_count(self):
        if self.fail_errors_count >= self.FAIL_TOLERANCE:
            self.fail(f"Command failed due to too many errors: {self.FAIL_TOLERANCE} errors")

    def fail(self, message):
        self.print_end_message()
        raise CommandError(message)
