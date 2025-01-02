from datetime import datetime

import pytest

from dynpy.logger.base import BaseLogger
from dynpy.logger.enums import LogStatus
from dynpy.logger.models import Log

pytestmark = pytest.mark.django_db


def get_base_logger(app_name=__package__ or "tests"):
    return BaseLogger(app_name=app_name)


def create_action_log(
    run_as="user",
    service_name="command",
    body="action performed",
    status=LogStatus.PASS,
):
    logger = get_base_logger()
    log = logger.log_action(run_as=run_as, service_name=service_name, body=body, status=status)
    return log


def test_that_it_logs_an_action():
    create_action_log()
    assert Log.objects.all().count() == 1


def test_that_log_properties_are_set_correctly():
    log = create_action_log()
    assert log.run_as == "user"
    assert log.service_name == "command"
    assert log.body == "action performed"
    assert log.status == LogStatus.PASS
    assert type(log.completed_at) == datetime


def test_that_completed_at_is_not_None():
    log = create_action_log()
    assert log.completed_at is not None
