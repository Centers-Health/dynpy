from dynpy_actions.templatetags.actions_tags import render_hash


def test_returns_correct_url_param(test_user, test_model_action, rf):
    request = rf.get("/")
    test_model_action = test_model_action()
    url_hash = render_hash({"request": request}, test_model_action, model_instance=test_user)
    expected_hash = f"action_hash={test_model_action.get_hash(request,model_instance = test_user)}"
    assert url_hash == expected_hash
