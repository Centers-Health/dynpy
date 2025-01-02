from dynpy_actions.actions import ViewActions

from dynpy_gfl.views import GenericFilterListWithActionsView


def test_action_appends_object_id_hash(
    test_form,
    test_user,
    rf,
):
    class TestAction(ViewActions):
        element = test_form
        name = "test_action"

        def handle(self, data, form, **kwargs):
            pass

    class TestView(GenericFilterListWithActionsView):
        actions = [TestAction]
        template_name = "dyn-actions/action_generic_base_form.html"

    request = rf.post(
        "/",
        {"action_name": "test_action", "model_instance_id": test_user.id},
    )
    response = TestView.as_view()(request)

    assert response.status_code == 302
    assert response.url == f"#{test_user.id}"


def test_action_does_not_append_object_id_hash_when_get_success_url_is_overridden(
    test_form,
    test_user,
    rf,
):
    class TestActionWithSuccessURL(ViewActions):
        element = test_form
        name = "test_action"

        def handle(self, data, form, **kwargs):
            pass

        def get_success_url(self, request):
            return "/dummy_path"

    class TestView(GenericFilterListWithActionsView):
        actions = [TestActionWithSuccessURL]
        template_name = "dyn-actions/action_generic_base_form.html"

    request = rf.post(
        "/",
        {"action_name": "test_action", "model_instance_id": test_user.id},
    )
    response = TestView.as_view()(request)

    assert response.status_code == 302
    assert response.url == "/dummy_path"
