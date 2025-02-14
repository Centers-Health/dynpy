import traceback

from dynpy.logger.base import BaseErrorLogger


class DWErrorLogger(BaseErrorLogger):
    """
    Logger to log the DW import errors
    """

    service_name = "dw_error"

    @property
    def error_message(self) -> str:
        error_message = (
            self.exception.message if hasattr(self.exception, "message") else str(self.exception)
        )
        return (
            f"Error in {self.erroring_command} : {self.exception.__class__.__name__} -> {error_message}"
        )


class UnexpectedErrorLogger(BaseErrorLogger):
    """
    Logger to log the unexpected errors
    """

    service_name = "unexpected_error"

    @property
    def error_message(self) -> str:
        error_message = (
            f"Error in {self.erroring_command} : {self.exception.__class__.__name__},\n {self.row}"
        )
        return error_message + "\n" + traceback.format_exc()
