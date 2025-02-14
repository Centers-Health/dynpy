import pytest
from dynpy.logger.enums import LogStatus
from dynpy.logger.loggers import DWErrorLogger
from dynpy.logger.models import Log


@pytest.mark.django_db
def test_dw_error_logger_sets_fields_correctly():
    DWErrorLogger(
        row=None, exception=Exception("this is a test error"), erroring_command="test command"
    ).log_action()
    log = Log.objects.first()

    assert log.status == LogStatus.FAIL
    assert log.service_name == "dw_error"
    assert log.body == "Error in test command : Exception -> this is a test error"
    assert log.run_as == ""
