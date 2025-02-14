import pytest
from tests.management.commands.success_logging_command import Command as SuccessLoggingCommand


def test_that_it_gets_the_service_name():
    slc = SuccessLoggingCommand()
    assert slc.get_service_name() == "success_logging_command"


def test_that_it_raises_an_error_if_service_name_is_None():
    slc = SuccessLoggingCommand()
    slc.service_name = None
    with pytest.raises(NotImplementedError):
        slc.get_service_name()
