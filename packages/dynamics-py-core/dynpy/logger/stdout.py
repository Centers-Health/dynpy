import contextlib
import io
import sys

from django.utils import dateformat, timezone


class TeeIO(io.StringIO):
    def __init__(self, original_target, new_target, is_timestamped: bool):
        self.original_target = original_target
        self.new_target = new_target
        self.is_timestamped = is_timestamped

    def write(self, message):
        """
        Write a message to both the `original_target` and `new_target`
        """
        message = self._prepend_timestamp(message)
        self.original_target.write(message)
        self.new_target.write(message)

    def _prepend_timestamp(self, message):
        """
        Conditionally add a timestamp to a message
        """
        messages_to_ignore = [
            # A new line character is sent separately after each message by default. If a timestamp is
            # prepended to it, it appears at the end of the previous line, which we do not want
            "\n"
        ]
        if self.is_timestamped and message not in messages_to_ignore:
            timestamp = dateformat.format(timezone.now(), "Y-m-d H:i:s.u")
            message = f"[{timestamp}]\t{message}"
        return message


@contextlib.contextmanager
def tee_stdout(new_target, is_timestamped: bool = False):
    """
    Grab all standard input and write to both standard output and another target

    Usage:

    ```
    buf = io.StringIO()
    with tee_stdout(buf):
        print("foo")  # this will print to the terminal and write to buf
    ```

    Based on StackOverflow answer here: https://stackoverflow.com/a/41580373/11278892

    Named after Linux `tee` command
    """
    tee = TeeIO(sys.stdout, new_target, is_timestamped)
    with contextlib.redirect_stdout(tee):
        yield
