import json

import pytest
from django.contrib.auth import get_user_model
from requests import HTTPError, Response

pytestmark = pytest.mark.django_db()
User = get_user_model()

# Helpers


def mock_response(content=None, status_code=None):
    response = Response()
    response._content = content
    response.status_code = status_code
    return response


def test_200_response_returns_json(mocker):
    from dynpy.graphql.graph_connector import GraphConnector

    # requests_mock.post(settings.GRAPH_URL, json={'data': 'someData'})
    mock_content = b'{"data": {"someQuery": "something"}}'
    response = mock_response(content=mock_content, status_code=200)
    mocker.patch("requests.post", return_value=response)

    results = GraphConnector().execute("someQuery")
    assert results == json.loads(mock_content)


def describe_JWT_cookie():
    def test_adds_JWT_cookie_if_request_has_user(mocker, rf, test_user):
        from dynpy.graphql.graph_connector import GraphConnector

        request = rf.get("/")
        request.user = test_user

        mock_content = b'{"data": {"someQuery": "something"}}'
        response = mock_response(content=mock_content, status_code=200)
        mock_post = mocker.patch("requests.post", return_value=response)

        GraphConnector(request).execute("someQuery")

        assert "JWT" in mock_post.call_args_list[-1].kwargs["cookies"]

    def does_not_add_if_request_does_not_have_user(mocker, rf):
        from dynpy.graphql.graph_connector import GraphConnector

        request = rf.get("/")

        mock_content = b'{"data": {"someQuery": "something"}}'
        response = mock_response(content=mock_content, status_code=200)
        mock_post = mocker.patch("requests.post", return_value=response)

        GraphConnector(request).execute("someQuery")

        assert "JWT" not in mock_post.call_args_list[-1].kwargs["cookies"]

    def does_not_add_if_no_request_is_passed(mocker, rf):
        from dynpy.graphql.graph_connector import GraphConnector

        mock_content = b'{"data": {"someQuery": "something"}}'
        response = mock_response(content=mock_content, status_code=200)
        mock_post = mocker.patch("requests.post", return_value=response)

        GraphConnector().execute("someQuery")

        assert "JWT" not in mock_post.call_args_list[-1].kwargs["cookies"]


@pytest.mark.django_db()
def test_not_ok_response_raises_error(mocker):
    from dynpy.graphql.graph_connector import GraphConnector

    response = mock_response(status_code=400)
    mocker.patch("requests.post", return_value=response)

    with pytest.raises(HTTPError):
        GraphConnector().execute("someQuery")
