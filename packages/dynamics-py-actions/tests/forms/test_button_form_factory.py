from dynpy_actions.forms import button_form_factory


def test_it_sets_the_content_of_the_button_to_inner_html():
    form = button_form_factory(inner_html="x")
    assert form().get_form_action().content == "x"


def test_it_sets_button_kwargs():
    form = button_form_factory(button_kwargs={"test": "x"})
    assert 'test="x"' in form().get_form_action().flat_attrs
