import pytest
from django.conf import settings

from dynpy.logger.module import get_app_name_from_module


@pytest.fixture
def mock_installed_apps(mocker):
    mocker.patch.object(
        settings,
        "INSTALLED_APPS",
        ["app", "app.subapp", "app.config_app.apps.AppConfig"],
    )


def test_that_it_can_match_a_top_level_app(mock_installed_apps):
    assert get_app_name_from_module("app.file") == "app"


def test_that_it_can_match_a_subapp(mock_installed_apps):
    assert get_app_name_from_module("app.subapp.file") == "app.subapp"


def test_that_it_can_match_app_with_config(mock_installed_apps):
    assert get_app_name_from_module("app.config_app.file") == "app.config_app"


def test_that_it_returns_None_if_no_matching_app_is_found(mock_installed_apps):
    assert get_app_name_from_module("invalid.module.path") is None
