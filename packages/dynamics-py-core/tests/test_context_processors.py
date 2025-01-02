from django.template import Context, Template

from dynpy.context_processors import env


def test_env_context_processor(mocker):
    mocker.patch("os.environ", {"TEST_VAR": "TEST_VALUE"})
    template = Template("{% load dynpy_tags %}{{TEST_VAR}}")
    response = template.render(Context(env()))
    assert "TEST_VALUE" in response
