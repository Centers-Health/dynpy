from django.http import HttpResponse
from django.template.loader import render_to_string


class HXConfirmMixin:
    """
    Mixin that returns a confirmation dynamically based on the form data.

    In order for this to work:
    - There must be an id set on the trigger element
    - An empty div with the id of the confirmation_placeholder_id must be present
    """

    confirmation_template = "dynpy_forms/confirmation.html"
    confirmation_placeholder_id = "confirmation-placeholder"
    confirmation_message: str

    def form_valid(self, **kwargs):
        # If the form submission is not confirmed, attempt to generate a confimation message.
        # If there is no confirmation message, the form will be submitted as normal.
        if self.confirmed is False and (message := self.get_confirmation_message(**kwargs)):
            return self.get_confirmation_response(message, **kwargs)
        return super().form_valid(**kwargs)

    @property
    def confirmed(self) -> bool:
        return self.request.headers.get("HX-Confirmed") == "true"

    def get_confirmation_message(self, **kwargs) -> str | None:
        if not hasattr(self, "confirmation_message"):
            raise NotImplementedError(
                "get_confirmation_message needs to be implemented or confirmation_message must be set"
            )
        return self.confirmation_message

    def get_confirmation_response(self, confirm_message: str, **kwargs) -> HttpResponse:
        headers = self.request.headers
        try:
            trigger_id = headers["HX-Trigger"]
        except KeyError as e:
            raise ValueError("Trigger element must have an id to use confirmation") from e

        url = headers["HX-Current-URL"]
        headers = {"HX-Retarget": f"#{self.confirmation_placeholder_id}"}
        context = {
            "confirm_message": confirm_message,
            "url": url,
            "source_id": trigger_id,
        }
        html = render_to_string(self.confirmation_template, context=context)
        return HttpResponse(html, headers=headers)
