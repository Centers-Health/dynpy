import pytest
from django.forms import modelformset_factory
from django.forms.models import BaseModelFormSet
from dynpy_actions.actions import ViewActions
from dynpy_actions.mixins import FormsetMixin


# ---------------------------------------------------------------------------- #
#                                    FIXTURES                                   #
# ---------------------------------------------------------------------------- #
@pytest.fixture
def action_with_formsets(test_form, django_user_model):
    formset = modelformset_factory(django_user_model, form=test_form)

    class TestActionWithFormsets(FormsetMixin, ViewActions):
        element = test_form
        formsets = {"my_formset": formset}

    return TestActionWithFormsets()


# ---------------------------------------------------------------------------- #
#                                     TESTS                                    #
# ---------------------------------------------------------------------------- #


def test_async_validate_returns_formset_errors(rf, action_with_formsets):
    # Arrange
    action = action_with_formsets
    invalid_username = "$#@q32"

    # Act
    request = rf.post(
        "/",
        data={
            "form-0-username": invalid_username,
            "form-INITIAL_FORMS": "0",
            "form-TOTAL_FORMS": "1",
        },
    )
    validation = action.async_validate(request, action_with_formsets.element(data=request.POST))

    # Assert
    username_error_message = validation.get("errors").get("form-0-username")[0].get("message")
    expected_error_message = "Enter a valid username. This value may contain only letters, numbers"
    assert expected_error_message in username_error_message


def test_can_override_dynamic_kwargs_function_to_set_kwargs(rf, django_user_model, test_form):
    class Formset(BaseModelFormSet):
        prefix = "test"

    formset = modelformset_factory(django_user_model, form=test_form, formset=Formset)

    class TestActionWithFormsets(FormsetMixin, ViewActions):
        element = test_form
        formsets = {"my_formset": formset}

        def get_my_formset_kwargs(self, request, model_instance):
            return {"prefix": "test"}

    action = TestActionWithFormsets()
    invalid_username = "$#@q32"

    # Act
    request = rf.post(
        "/",
        data={
            "test-0-username": invalid_username,
            "test-INITIAL_FORMS": "0",
            "test-TOTAL_FORMS": "1",
        },
    )
    validation = action.async_validate(request, action.element(data=request.POST))

    # Assert
    username_error_message = validation.get("errors").get("test-0-username")[0].get("message")
    expected_error_message = "Enter a valid username. This value may contain only letters, numbers"
    assert expected_error_message in username_error_message


def test_can_override_dynamic_kwargs_function_to_set_kwargs_when_have_multiple_formsets(
    rf, django_user_model, test_form
):
    class Formset(BaseModelFormSet):
        prefix = "formset1"

    class Formset2(BaseModelFormSet):
        prefix = "formset"

    formset = modelformset_factory(django_user_model, form=test_form, formset=Formset)
    formset2 = modelformset_factory(django_user_model, form=test_form, formset=Formset2)

    class TestActionWithFormsets(FormsetMixin, ViewActions):
        element = test_form
        formsets = {"formset1": formset, "formset2": formset2}

        def get_formset1_kwargs(self, request, model_instance):
            return {"prefix": "formset1"}

        def get_formset2_kwargs(self, request, model_instance):
            return {"prefix": "formset2"}

    action = TestActionWithFormsets()
    invalid_username = "$#@q32"

    # Act
    request = rf.post(
        "/",
        data={
            "formset1-0-username": invalid_username,
            "formset1-INITIAL_FORMS": "0",
            "formset1-TOTAL_FORMS": "1",
            "formset2-0-username": invalid_username,
            "formset2-INITIAL_FORMS": "0",
            "formset2-TOTAL_FORMS": "1",
        },
    )
    validation = action.async_validate(request, action.element(data=request.POST))

    # Assert
    formset1_error_message = validation.get("errors").get("formset1-0-username")[0].get("message")
    formset2_error_message = validation.get("errors").get("formset1-0-username")[0].get("message")
    expected_error_message = "Enter a valid username. This value may contain only letters, numbers"
    assert expected_error_message in formset1_error_message
    assert expected_error_message in formset2_error_message
