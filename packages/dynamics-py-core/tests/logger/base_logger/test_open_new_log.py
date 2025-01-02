import pytest

from dynpy.logger.base import BaseLogger
from dynpy.logger.enums import LogStatus
from dynpy.logger.models import Log

pytestmark = pytest.mark.django_db


def get_base_logger(app_name=__package__ or "tests"):
    return BaseLogger(app_name=app_name)


def open_new_log(run_as="user", service_name="long-running command", body=""):
    logger = get_base_logger()
    log = logger.open_new_log(run_as=run_as, service_name=service_name, body=body)
    return log


def test_that_it_opens_a_new_log():
    open_new_log()
    assert Log.objects.all().count() == 1


def test_that_log_properties_are_set_correctly():
    log = open_new_log()
    assert log.completed_at is None
    assert log.body == ""
    assert log.run_as == "user"
    assert log.status == LogStatus.PEND
    assert log.service_name == "long-running command"


def test_that_body_defaults_to_empty_string():
    logger = get_base_logger()
    log = logger.open_new_log(run_as="user", service_name="long-running command")
    assert log.body == ""
