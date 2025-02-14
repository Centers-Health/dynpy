import pytest
from django.core.management import call_command

from dynpy.logger.models import Log

pytestmark = pytest.mark.django_db


def test_that_run_as_defaults_to_empty_string():
    call_command("success_logging_command")
    assert Log.objects.last().run_as == ""


def test_that_run_as_is_set_on_the_log_if_it_is_set_in_the_command():
    call_command("success_logging_command", run_as="user")
    assert Log.objects.last().run_as == "user"
