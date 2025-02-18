import pytest

from dynpy_forms.form_mixins import HXConfirmMixin

htmx_headers = {
    "HTTP_HX-Request": "true",
    "HTTP_HX-Trigger": "trigger-id",
    "HTTP_HX-Current-URL": "http://example.com",
}


class FakeHXRequest:
    def __init__(self, request) -> None:
        self.request = request

    def form_valid(self, **kwargs):
        pass


class ConfirmFormView(HXConfirmMixin, FakeHXRequest):
    def get_confirmation_message(self, **kwargs):
        return "Are you sure?"


def test_returns_confirmation_when_get_confirmation_message_returns_str(rf):
    response = ConfirmFormView(rf.post("/", **htmx_headers)).form_valid()
    assert "Are you sure?" in response.content.decode()


def test_does_not_return_confirmation_when_get_confirmation_message_returns_None(mocker, rf):
    mocker.patch.object(ConfirmFormView, "get_confirmation_message", return_value=None)
    mock_form_valid = mocker.patch.object(FakeHXRequest, "form_valid")

    ConfirmFormView(rf.post("/", **htmx_headers)).form_valid()

    mock_form_valid.assert_called_once()


def test_confirmation_template_has_url(rf):
    request = rf.post("/", **htmx_headers)
    response = ConfirmFormView(request).form_valid()
    url = request.headers["HX-Current-URL"]

    assert url in response.content.decode()


def test_confirmation_template_has_source_id(rf):
    request = rf.post("/", **htmx_headers)
    response = ConfirmFormView(request).form_valid()
    source_id = request.headers["HX-Trigger"]

    assert source_id in response.content.decode()


def test_raises_error_if_no_hx_trigger_id(rf):
    headers = htmx_headers.copy()
    headers.pop("HTTP_HX-Trigger")
    request = rf.post("/", **headers)

    with pytest.raises(ValueError, match="Trigger element must have an id to use confirmation"):
        ConfirmFormView(request).form_valid()


def test_confirmation_response_targets_placeholder_id(rf):
    response = ConfirmFormView(rf.post("/", **htmx_headers)).form_valid()
    placeholder_id = ConfirmFormView.confirmation_placeholder_id

    assert response.headers["HX-Retarget"] == f"#{placeholder_id}"


def test_raises_error_if_confirmation_message_is_not_set(mocker, rf):
    class InvalidView(HXConfirmMixin, FakeHXRequest):
        def needs_confirmation(self, **kwargs):
            return True

    with pytest.raises(
        NotImplementedError,
        match="get_confirmation_message needs to be implemented or confirmation_message must be set",
    ):
        InvalidView(rf.post("/", **htmx_headers)).form_valid()
