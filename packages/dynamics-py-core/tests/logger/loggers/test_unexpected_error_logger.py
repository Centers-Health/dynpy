import pytest
from dynpy.logger.enums import LogStatus
from dynpy.logger.loggers import UnexpectedErrorLogger
from dynpy.logger.models import Log


@pytest.mark.django_db
def test_dw_error_logger_sets_fields_correctly():
    UnexpectedErrorLogger(
        row={"test": "test"},
        exception=Exception("this is a test error"),
        erroring_command="test command",
    ).log_action()
    log = Log.objects.first()

    assert log.status == LogStatus.FAIL
    assert log.service_name == "unexpected_error"
    assert "Error in test command : Exception" in log.body
    assert str({"test": "test"}) in log.body
    assert log.run_as == ""
