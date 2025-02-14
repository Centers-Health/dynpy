import io
from datetime import datetime

import pytest
from dynpy.logger.stdout import tee_stdout

"""
Helpers
"""


def get_message_timestamp(buf: io.StringIO) -> str:
    line1 = buf.getvalue().split("\n")[0]
    timestamp = line1.split("\t")[0]
    for character in ["[", "]"]:
        timestamp = timestamp.replace(character, "")
    return timestamp


"""
Tests
"""


def test_it_prepends_timestamp(capfd, mocker):
    buf = io.StringIO()
    with tee_stdout(buf, is_timestamped=True):
        print("test message")
    timestamp = get_message_timestamp(buf)
    # make sure it is a valid timestamp
    datetime.fromisoformat(timestamp)


def test_new_line_does_not_get_timestamped(capfd, mocker):
    buf = io.StringIO()
    with tee_stdout(buf, is_timestamped=True):
        print("\n")
    not_timestamp = get_message_timestamp(buf)
    with pytest.raises(ValueError):
        datetime.fromisoformat(not_timestamp)
