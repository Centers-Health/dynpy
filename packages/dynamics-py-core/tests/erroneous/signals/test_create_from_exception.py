import pytest
from django.urls import reverse

from dynpy.erroneous.models import Error

pytestmark = pytest.mark.django_db


def test_creates_erroneous_error(client):
    with pytest.raises(AttributeError):
        client.get(reverse("dummy_error"))
    assert Error.objects.count() == 1


def test_calls_log_erroneous_error(client, mocker):
    # Arrange
    mocked_log_erroneous_error = mocker.patch(
        "dynpy.erroneous.signals.log_erroneous_error", return_value=None
    )

    with pytest.raises(AttributeError):
        client.get(reverse("dummy_error"))

    mocked_log_erroneous_error.assert_called_once()
