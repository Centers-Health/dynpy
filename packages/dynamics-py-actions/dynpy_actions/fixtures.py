from typing import Dict, Optional

import pytest
from django.db.models.base import Model

"""
    To use fixtures from here in a project add this file as a Pytest plugin.
    One way to do this is to add the following line in conftest.py:
        pytest_plugins = "dynpy_actions.fixtures"
"""


@pytest.fixture
def handle_action(rf, add_middleware_to_request):
    def _handle_action(action, user=None, additional_form_data: Optional[Dict] = None, **kwargs):
        additional_form_data = additional_form_data or {}
        GET_request = rf.get("/")
        GET_request.user = user
        form = action.get_initialized_form(GET_request, data=additional_form_data, **kwargs)
        post_data = {**form.initial, **form.data}
        # Need to turn model instances into pk's for post data
        for k, v in post_data.items():
            if isinstance(v, Model):
                post_data[k] = v.pk
            if v is None:
                post_data[k] = ""

        POST_request = rf.post("/", data=post_data)
        POST_request.user = user
        add_middleware_to_request(POST_request)
        return action.handle(POST_request)

    return _handle_action
