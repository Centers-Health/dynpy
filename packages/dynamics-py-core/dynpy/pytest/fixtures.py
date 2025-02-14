import pytest
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save

from dynpy.dw import DWConnector
from dynpy.pytest.ncs_mockers import Cursor

"""
    To use fixtures from here in a project add this file as a Pytest plugin.
    One way to do this is to add the following line in conftest.py:
        pytest_plugins = "dynpy.pytest.fixtures"
"""


@pytest.fixture()
def mock_sp(mocker):
    """
    Mock an sp by name.
    Takes an sp and a list of mock data to be returned
    Example:
        mock_sp(
            sp="{CALL usp_Refresh_NamiPrivate_Aging_4}",
            data=[ncs_mockers.AgingRow()]
        )

    TODO: Add ability to return different data depending on what args are passed to SPs that take additional arguments
    """

    def _mock_sp(sp: str, data: list):
        original_run_sp = DWConnector().run_sp
        sp_to_mock = sp

        def side_effect(*args, **kwargs):
            queried_sp = kwargs["sp"] if "sp" in kwargs else args[0]
            if queried_sp == sp_to_mock:
                return Cursor(data=data)
            else:
                return original_run_sp(DWConnector(), sp=queried_sp)

        mocker.patch("dynpy.dw.DWConnector.run_sp", side_effect=side_effect)

    return _mock_sp


@pytest.fixture()
def add_middleware_to_request():
    def _add_middleware_to_request(request):
        request.session = "session"
        messages = FallbackStorage(request)
        request._messages = messages

        return request

    return _add_middleware_to_request


# source: https://www.cameronmaske.com/muting-django-signals-with-a-pytest-fixture/
@pytest.fixture()
def _dynpy_mute_signals(request):
    # Skip applying, if marked with `enabled_signals` (@pytest.mark.enable_signals)
    if "enable_signals" in request.keywords:
        yield
    else:
        signals = [pre_save, post_save, pre_delete, post_delete, m2m_changed]
        restore = {}
        for signal in signals:
            # Temporally remove the signal's receivers
            restore[signal] = signal.receivers
            signal.receivers = []

        def restore_signals():
            # When the test tears down, restore the signals.
            for signal, receivers in restore.items():
                signal.receivers = receivers

        yield
        # Called after a test has finished.
        restore_signals()


@pytest.fixture()
def test_file():
    return SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")


@pytest.fixture()
@pytest.mark.django_db()
def dyn_superuser(django_user_model):
    # authenticated_client vars
    username = "test_superuser"
    password = "test_password"
    email = "test_superuser@email.com"

    # create normal main test user
    user = django_user_model.objects.create(
        username=username,
        email=email,
    )
    user.set_password(password)
    user.is_superuser = True
    user.save()
    user.refresh_from_db()

    return user
