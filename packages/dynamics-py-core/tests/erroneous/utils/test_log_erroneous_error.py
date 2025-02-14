import pytest
from dateutil.relativedelta import relativedelta
from django.test.utils import override_settings
from django.utils import timezone

from dynpy.erroneous.models import Error
from dynpy.erroneous.utils import log_erroneous_error

pytestmark = pytest.mark.django_db


def test_creates_error():
    # Arrange
    kind = "test_kind"
    html = "test_html"
    info = "test_info"
    data = "test_data"
    path = "test_path"

    # Act
    log_erroneous_error(kind=kind, html=html, info=info, data=data, path=path)

    # Assert
    assert Error.objects.count() == 1
    err = Error.objects.first()
    assert err.kind == kind
    assert err.html == html
    assert err.info == info
    assert err.data == data
    assert err.path == path


def test_wont_log_same_error_twice_in_one_day(mocker):
    """
    The hash is a combination of the stacktrace and today's date
    therefore it should not log the same error twice on one day.
    """
    # Arrange
    # Mock timezone.now to make sure it is the same day for the second error
    today = timezone.now()
    mocker.patch.object(timezone, "now", return_value=today)

    # Act
    log_erroneous_error(kind="", html="", info="", data="", path="")
    log_erroneous_error(kind="", html="", info="", data="", path="")

    # Assert
    assert Error.objects.count() == 1


def test_duplicate_error_on_same_day_increments_counter(mocker):
    # Arrange
    # Mock timezone.now to make sure it is the same day for the second error
    today = timezone.now()
    mocker.patch.object(timezone, "now", return_value=today)

    # Act
    log_erroneous_error(kind="", html="", info="", data="", path="")
    log_erroneous_error(kind="", html="", info="", data="", path="")

    # Assert
    assert Error.objects.last().count == 2


def test_duplicate_error_on_new_day_creates_new_instance(mocker):
    # Arrange
    # Mock timezone.now to make sure it is the same day for the second error
    tomorrow = timezone.now() + relativedelta(days=+1)

    # Act
    log_erroneous_error(kind="", html="", info="", data="", path="")
    mocker.patch.object(timezone, "now", return_value=tomorrow)
    log_erroneous_error(kind="", html="", info="", data="", path="")

    # Assert
    assert Error.objects.count() == 2


@override_settings(DEBUG=True)
def test_only_logs_errors_when_NOT_in_debug_mode():
    """
    In debug mode we don't want to log the Errors.
    """
    log_erroneous_error(kind="", html="", info="", data="", path="")
    assert Error.objects.count() == 0
