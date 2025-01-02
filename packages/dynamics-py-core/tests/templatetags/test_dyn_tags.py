import os

import pytest
from django.conf import settings
from django.template import Context, Template
from django.test.client import RequestFactory
from django.utils.http import urlencode

from dynpy.templatetags.dynpy_tags import (
    env,
    field_name_to_label,
    get_dict_value,
    get_obj_attr,
    param_replace,
    redirect_back,
    to_str,
)

rf = RequestFactory()


def test_base_url(mocker):
    mocker.patch("os.environ", {"BASE_URL": "https://ar.localhost"})
    settings.BASE_URL = os.getenv("BASE_URL")
    template = Template("{% load dynpy_tags %} " "{% base_url 'home' %} ")
    response = template.render(Context())
    assert "https://ar.localhost/home" in response


def test_get_absolute_static_url(mocker):
    mocker.patch("os.environ", {"BASE_URL": "https://ar.localhost"})
    settings.BASE_URL = os.getenv("BASE_URL")
    template = Template("{% load dynpy_tags %} " "{% absolute_static 'img/testImage.jpg' %} ")
    response = template.render(Context())
    assert "https://ar.localhost/static/img/testImage.jpg" in response


def test_env_filter(mocker):
    mocker.patch("os.environ", {"TEST_VAR": "TEST_VALUE"})
    assert env("TEST_VAR") == "TEST_VALUE"


def describe_get_dict_value():
    def it_returns_value_based_on_key():
        dict = {"a": 1, "b": 2}
        assert get_dict_value(dict, "a") == 1
        assert get_dict_value(dict, "b") == 2

    def it_returns_None_when_key_is_not_in_dict():
        dict = {"a": 1, "b": 2}
        assert get_dict_value(dict, "c") is None


def describe_get_obj_attr():
    def it_returns_value_based_on_attr():
        class Test:
            pass

        obj = Test()
        obj.a = 1
        obj.b = 2

        assert get_obj_attr(obj, "a") == 1
        assert get_obj_attr(obj, "b") == 2

    def it_returns_None_when_object_does_not_have_the_attr():
        class Test:
            pass

        obj = Test()
        obj.a = 1
        obj.b = 2
        assert get_obj_attr(obj, "c") is None


def test_that_it_passes_the_whole_url_encoded_as_one_parameter():
    test_url = "/somepage?v1=100&p1=30"
    context = {"request": rf.get(test_url)}
    assert redirect_back(context) == f"?{urlencode({'redirect_back':test_url})}"


@pytest.mark.parametrize(
    ("field_name", "expected"),
    [
        ("user", "User"),
        ("user_email", "User Email"),
        ("USER", "User"),
        ("USER_EMAIL", "User Email"),
        ("BILLING_name", "Billing Name"),
        ("BILLING_name_name", "Billing Name Name"),
    ],
)
def test_that_passing_in_a_field_name_converts_to_a_label(field_name, expected):
    assert field_name_to_label(field_name) == expected


@pytest.mark.parametrize(
    ("field_name", "expected"),
    [
        ("user__sssss", "User Sssss"),
    ],
)
def test_that_relationship_fields_do_not_create_extra_spaces(field_name, expected):
    assert field_name_to_label(field_name) == expected


@pytest.mark.parametrize(("field_name", "expected"), [("   user   ", "User")])
def test_that_whitespace_is_trimmed(field_name, expected):
    assert field_name_to_label(field_name) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (5, "5"),
        ("5", "5"),
        (None, ""),
    ],
)
def test_that_it_converts_int_or_none_to_a_str(value, expected):
    assert to_str(value) == expected


def test_that_it_appends_the_value_keeping_the_other_values():
    test_url = "/somepage?v1=100&p1=30"
    get_request = rf.get(test_url)
    context = {"request": get_request}
    assert "hello=10" in param_replace(context, hello=10)


def test_that_it_replaces_its_own_value_instead_of_duplicating_it():
    test_url = "/somepage?v1=100&p1=30&hello=4"
    get_request = rf.get(test_url)
    context = {"request": get_request}
    assert "hello=10" in param_replace(context, hello=10)
    assert "hello=4" not in param_replace(context, hello=10)


def test_that_it_can_append_multiple_params():
    test_url = "/somepage?v1=100&p1=30&hello=4"
    get_request = rf.get(test_url)
    context = {"request": get_request}
    result = param_replace(context, v1="bob", p1="50")
    assert "v1=bob" in result
    assert "v1=100" not in result
    assert "p1=50" in result
    assert "p1=30" not in result
