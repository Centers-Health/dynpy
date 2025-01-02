from io import BytesIO
from unittest.mock import MagicMock, Mock

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.http.response import FileResponse, HttpResponse, JsonResponse
from django.urls import reverse

from dynpy_cas.enums import Codename
from dynpy_cas.middleware import ReadOnlyMiddleware

pytestmark = pytest.mark.django_db()
User = get_user_model()


# Fixtures
@pytest.fixture(autouse=True)
def _override_settings_for_testing_middleware(settings):
    settings.MIDDLEWARE.append("dynpy_cas.middleware.ReadOnlyMiddleware")


@pytest.fixture(autouse=True)
def _mock_resolve(mocker):
    mock_resolve = MagicMock()
    mock_resolve.app_name = "aging"
    mocker.patch("dynpy_cas.middleware.resolve", return_value=mock_resolve)


@pytest.fixture()
def test_user_with_edit_permission(test_user):
    editor_perm = Permission.objects.get(codename=Codename.AGING_EDITOR)
    test_user.user_permissions.add(editor_perm)
    return test_user


@pytest.fixture()
def test_user_with_no_permissions(django_user_model):
    user = django_user_model.objects.create(username="test_username", first_name="John", last_name="Doe")
    user.set_password("test_password")
    user.save()
    user.refresh_from_db()

    return user


# Tests
def describe_read_only_middleware():
    def it_allows_get_requests_to_pass_through(rf, test_user_with_no_permissions):
        request = rf.get("/")
        request.user = test_user_with_no_permissions

        get_response_mock = Mock(return_value=HttpResponse(b""))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert response.status_code == 200

    def it_allows_READ_ONLY_ALLOWED_URLS_from_settings(rf, test_user_with_no_permissions, settings):
        settings.READ_ONLY_ALLOWED_URLS = ["dashboard"]
        request = rf.post(reverse("dashboard"))
        request.user = test_user_with_no_permissions

        get_response_mock = Mock(return_value=HttpResponse(b""))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert response.status_code == 200

    def it_redirects_if_missing_editor_perm_and_has_http_referer(
        rf, test_user_with_no_permissions, mocker
    ):
        request = rf.post("/")
        request.user = test_user_with_no_permissions
        request.META["HTTP_REFERER"] = reverse("dashboard")

        message = mocker.patch("dynpy_cas.middleware.messages.error")

        get_response_mock = Mock(return_value=HttpResponse(b""))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert response.url == request.path
        assert response.status_code == 302
        assert message.called_once()

    def it_redirects_if_missing_editor_perm_and_does_not_have_http_referer(
        rf, test_user_with_no_permissions, mocker
    ):
        request = rf.post("/")
        request.user = test_user_with_no_permissions

        message = mocker.patch("dynpy_cas.middleware.messages.error")

        get_response_mock = Mock(return_value=HttpResponse(b""))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert response.url == "/accounts/profile/"
        assert response.status_code == 302
        assert message.called_once()

    def it_allows_post_request_if_user_has_editor_perm(rf, test_user_with_edit_permission):
        request = rf.post("")
        request.user = test_user_with_edit_permission
        get_response_mock = Mock(return_value=HttpResponse(b""))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert response.status_code == 200

    def it_hides_submit_buttons_in_post_forms_if_user_does_not_have_edit_permission(
        rf, test_user_with_no_permissions
    ):
        content = (
            b'<form method="post">'
            b'  <button type="submit">Submit</button><input type="submit" value="Submit">'
            b"</form>"
        )
        request = rf.get("/")
        request.user = test_user_with_no_permissions
        get_response_mock = Mock(return_value=HttpResponse(content))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        soup = BeautifulSoup(response.content)
        submit_btns = soup.select('form [type="submit"]')

        assert len(submit_btns) == 0

    def it_shows_submit_buttons_in_post_forms_if_user_does_not_have_edit_permission_and_url_is_in_allowed_urls(
        rf, test_user_with_no_permissions, settings
    ):
        settings.READ_ONLY_ALLOWED_URLS = ["dashboard"]
        content = (
            b'<form method="post">'
            b'  <button type="submit">Submit</button><input type="submit" value="Submit">'
            b"</form>"
        )
        request = rf.get(reverse("dashboard"))
        request.user = test_user_with_no_permissions
        get_response_mock = Mock(return_value=HttpResponse(content))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        soup = BeautifulSoup(response.content)
        submit_btns = soup.select('form [type="submit"]')

        assert len(submit_btns) == 2

    def it_shows_submit_buttons_in_get_forms_if_user_does_not_have_edit_permission(
        rf, test_user_with_no_permissions
    ):
        content = (
            b'<form method="get">'
            b'  <button type="submit">Submit</button><input type="submit" value="Submit">'
            b"</form>"
        )
        request = rf.get("/")
        request.user = test_user_with_no_permissions
        get_response_mock = Mock(return_value=HttpResponse(content))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        soup = BeautifulSoup(response.content)
        submit_btns = soup.select('form [type="submit"]')

        assert len(submit_btns) == 2

    def it_shows_submit_buttons_in_post_forms_if_user_has_edit_permission(
        rf, test_user_with_edit_permission
    ):
        request = rf.get("/")
        request.user = test_user_with_edit_permission
        content = (
            b'<form method="post">'
            b'  <button type="submit">Submit</button><input type="submit" value="Submit">'
            b"</form>"
        )
        get_response_mock = Mock(return_value=HttpResponse(content))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        soup = BeautifulSoup(response.content)
        submit_btns = soup.select('form [type="submit"]')

        assert len(submit_btns) == 2

    def it_disables_inputs_in_post_forms_if_user_does_not_have_edit_permission(
        rf, test_user_with_no_permissions
    ):
        request = rf.get("/")
        request.user = test_user_with_no_permissions
        content = (
            b'<form method="post">'
            b"  <input><textarea></textarea><select></select><button></button>"
            b"</form>"
        )
        get_response_mock = Mock(return_value=HttpResponse(content))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        soup = BeautifulSoup(response.content)
        fields = soup.select("input,select,textarea,button")

        assert all("disabled" in f.attrs for f in fields)

    def it_does_not_disable_inputs_in_get_forms_if_user_does_not_have_edit_permission(
        rf, test_user_with_no_permissions
    ):
        request = rf.get("/")
        request.user = test_user_with_no_permissions
        content = (
            b'<form method="get">'
            b"  <input><textarea></textarea><select></select><button></button>"
            b"</form>"
        )
        get_response_mock = Mock(return_value=HttpResponse(content))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert "disabled" not in str(response.content)

    def it_does_not_disable_inputs_in_post_forms_if_user_has_edit_permission(
        rf, test_user_with_edit_permission
    ):
        request = rf.get("/")
        request.user = test_user_with_edit_permission
        content = (
            b'<form method="post">'
            b"  <input><textarea></textarea><select></select><button></button>"
            b"</form>"
        )
        get_response_mock = Mock(return_value=HttpResponse(content))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert "disabled" not in str(response.content)

    def it_does_not_interfere_with_json_responses(rf, test_user_with_no_permissions):
        request = rf.get("/")
        request.user = test_user_with_no_permissions
        json_response = JsonResponse({"test": "test"})
        get_response_mock = Mock(return_value=json_response)
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert response.status_code == 200
        assert response.content == b'{"test": "test"}'

    def it_does_not_interfere_with_file_responses(rf, test_user_with_no_permissions):
        request = rf.get("/")
        request.user = test_user_with_no_permissions
        file_response = FileResponse(BytesIO(b"test"), filename="test.txt")
        get_response_mock = Mock(return_value=file_response)
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert response.status_code == 200
        assert b"".join(response.streaming_content) == b"test"

    def it_does_not_add_html_and_body_tags(rf, test_user_with_no_permissions):
        """Regression test"""

        request = rf.get("/")
        request.user = test_user_with_no_permissions
        content = b"test"
        get_response_mock = Mock(return_value=HttpResponse(content))
        response = ReadOnlyMiddleware(get_response_mock)(request)

        assert response.content == content
