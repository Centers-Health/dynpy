import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_that_run_method_is_required():
    with pytest.raises(NotImplementedError):
        call_command("no_run_logging_command")
