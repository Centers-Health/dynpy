from dynpy.logger.enums import LogStatus
from dynpy.logger.models import Log


class BaseLogger:
    app_name: str

    def __init__(self, app_name: str = None) -> None:
        self.app_name = app_name or getattr(self, "app_name", None)
        if not self.app_name:
            raise ValueError("app_name must be set in the child class or passed as an argument")

    def log_action(self, run_as: str, service_name: str, body: str, status: LogStatus):
        """
        Logs a single action to the database and marks it as complete by setting the completed_at
        property to now
        """
        return Log.objects.create(
            app_name=self.app_name,
            body=body,
            run_as=run_as,
            service_name=service_name,
            status=status,
        )

    def open_new_log(self, run_as: str, service_name: str, body: str = ""):
        """
        Logs the beginning of a long-running command. Creates a new log instance in the database and
        returns it, to be updated while the command is running and/or when the command is completed.

        When using this method, make sure to set the log's completed_at property to the current datetime
        at the end of the command to mark the log as complete
        """
        return Log.objects.create(
            app_name=self.app_name,
            body=body,
            run_as=run_as,
            service_name=service_name,
            completed_at=None,
        )


class BaseErrorLogger(BaseLogger):
    """
    Class to log errors to the database. Child classes must
    implement set_error_message to set the error message for the
    specific type of logger.

    Status is always fail.

    Meant to be used in conjunction with the ExceptionLoggingCommand.
    Therefore it takes in the row, exception and erroring_command.

    """

    app_name = "Error"
    service_name: str
    row: any
    exception: Exception
    erroring_command: str

    def __init__(self, row, exception: Exception, erroring_command: str) -> None:
        super().__init__()
        if not self.service_name:
            raise ValueError("service_name must be set in the child class.")
        self.row = row
        self.exception = exception
        self.erroring_command = erroring_command

    @property
    def error_message(self) -> str:
        """
        Must be implemented in the child class.
        Use self.row, self.exception and self.erroring_command to craft the error message.
        """
        raise NotImplementedError("error_message must be implemented in the child class")

    def log_action(
        self,
        run_as: str = "",
    ):
        return super().log_action(run_as, self.service_name, self.error_message, LogStatus.FAIL)
