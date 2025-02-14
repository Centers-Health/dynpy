import io

import pytest

from dynpy.logger.stdout import tee_stdout


@pytest.fixture
def test_tee_buffer():
    buf = io.StringIO()
    with tee_stdout(buf):
        print("test message")
    return buf


def test_it_writes_to_inputted_buffer(test_tee_buffer):
    assert "test message" in test_tee_buffer.getvalue()


def test_it_prints_to_console(capfd, test_tee_buffer):
    capture = capfd.readouterr()
    assert "test message" in capture.out


def test_it_prints_to_console_after_command_completed(capfd, test_tee_buffer):
    message = "message after command complete"
    print(message)
    capture = capfd.readouterr()
    assert message in capture.out
