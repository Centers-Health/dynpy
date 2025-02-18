from crispy_forms.bootstrap import StrictButton
from django import forms

from dynpy_actions.constants import DEFAULT_ARG


def button_form_factory(inner_html="", button_kwargs=DEFAULT_ARG):
    button_kwargs = (
        button_kwargs if button_kwargs != DEFAULT_ARG else {"css_class": "btn btn-sm btn-primary"}
    )

    class BaseButtonActionForm(forms.Form):
        """
        Base button form for actions that are just a single button.
        Takes inner_html argument for the html to be displayed inside the button
        and an attr (attributes) dict to be applied to the button.

        CSS classes need to be passed in to the attr dict as 'css_class'.

        The arguments can be passed in via the get_form_kwargs method in the action
        so you can use this form as the element for the action directly.
        """

        def get_form_action(self):
            return StrictButton(inner_html, type="submit", **button_kwargs)

    return BaseButtonActionForm
