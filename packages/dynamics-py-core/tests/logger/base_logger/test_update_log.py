from datetime import datetime

import pytest
from dynpy.logger.base import BaseLogger
from dynpy.logger.enums import LogStatus

pytestmark = pytest.mark.django_db


def get_base_logger(app_name=__package__ or "tests"):
    return BaseLogger(app_name=app_name)


logger = get_base_logger()


def open_new_log(run_as="user", service_name="long-running command"):
    log = logger.open_new_log(run_as=run_as, service_name=service_name)
    return log


def test_that_it_updates_log_properties():
    log = open_new_log()
    log.update(body="completed body", is_completed=True, status=LogStatus.PASS)
    assert type(log.completed_at) == datetime
    assert log.body == "completed body"
    assert log.status == LogStatus.PASS


def test_that_completed_at_is_None_if_is_compelted_is_False():
    log = open_new_log()
    log.update(body="completed body", is_completed=False, status=LogStatus.PASS)
    assert log.completed_at is None
