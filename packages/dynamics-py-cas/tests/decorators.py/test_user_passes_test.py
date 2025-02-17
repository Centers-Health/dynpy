from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.api import get_messages
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from dynpy_cas.decorators import default_message, user_passes_test


@method_decorator(user_passes_test(lambda u: u.is_active), name="dispatch")
class TestView(View):
    def get(self, request):
        return HttpResponse("result")


def test_renders_view_if_user_passes_test(rf, test_user):
    request = rf.get("/")
    request.user = test_user

    # Act
    response = TestView.as_view()(request)

    # Assert
    assert response.status_code == 200


def test_redirects_to_login_redirect_url_if_user_does_not_pass_test_but_is_logged_in(
    rf, test_user, add_middleware_to_request
):
    request = rf.get("/")
    test_user.is_active = False
    request.user = test_user
    add_middleware_to_request(request)

    # Act
    response = TestView.as_view()(request)

    # Assert
    assert response.status_code == 302
    assert response.url == settings.LOGIN_REDIRECT_URL


def test_redirects_to_login_url_if_user_does_not_pass_test_and_is_not_logged_in(
    rf, add_middleware_to_request
):
    request = rf.get("/")
    request.user = AnonymousUser()
    add_middleware_to_request(request)

    # Act
    response = TestView.as_view()(request)

    # Assert
    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_adds_message_if_user_does_not_pass_test(rf, test_user, add_middleware_to_request):
    request = rf.get("/")
    test_user.is_active = False
    request.user = test_user
    add_middleware_to_request(request)

    # Act
    TestView.as_view()(request)

    # Assert
    assert get_messages(request)._queued_messages[0].message == default_message


def test_does_not_add_message_if_user_is_not_logged_in(rf, add_middleware_to_request):
    """
    If the user is not logged in they get redirected to cas. "Unauthorized"
    messages will only show up once they are redirected back to the redirect URL after
    logging in, and then the message isn't relevant anymore
    """
    request = rf.get("/")
    request.user = AnonymousUser()
    add_middleware_to_request(request)

    # Act
    TestView.as_view()(request)

    # Assert
    assert not get_messages(request)._queued_messages
