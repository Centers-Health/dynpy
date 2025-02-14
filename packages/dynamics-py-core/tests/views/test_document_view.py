import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse
from dynpy.views import MediaFileView
from tests.models import DocumentTestModel

pytestmark = pytest.mark.django_db


# Helper
def make_document():
    file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
    document = DocumentTestModel(file=file)
    document.save()
    return document


# Tests
def test_returns_files_browser_can_open_as_file_response(rf, test_user):
    document = make_document()

    request = rf.get(document.file.url)
    request.user = test_user
    response = MediaFileView.as_view()(request)

    assert isinstance(response, FileResponse)
    assert response.getvalue() == document.file.read()


def test_downloads_file_when_force_download_is_true(rf, test_user):
    class DocumentDownloadTestView(MediaFileView):
        force_download = True

    document = make_document()

    request = rf.get(document.file.url)
    request.user = test_user
    response = DocumentDownloadTestView.as_view()(request)

    assert isinstance(response, FileResponse)
    assert response.headers["Content-Type"] == "application/octet-stream"
    assert response.getvalue() == document.file.read()


def test_it_should_return_403_if_the_user_is_not_logged_in(rf):
    """It should redirect to login if the user is not logged in"""
    document = make_document()

    request = rf.get(document.file.url)
    request.user = lambda: None
    request.user.is_authenticated = False
    response = MediaFileView.as_view()(request)

    assert response.status_code == 403


def test_it_returns_file_response_for_non_authenticated_user_if_authentication_required_is_false(
    rf,
):
    class DocumentNonAuthenticatedTestView(MediaFileView):
        authentication_required = False

    document = make_document()

    request = rf.get(document.file.url)
    request.user = lambda: None
    request.user.is_authenticated = False
    response = DocumentNonAuthenticatedTestView.as_view()(request)

    assert isinstance(response, FileResponse)
    assert response.getvalue() == document.file.read()
