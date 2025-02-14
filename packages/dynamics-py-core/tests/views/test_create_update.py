import pytest
from django.http.response import Http404
from dynpy.views import CreateUpdateView
from tests.models import CreateUpdateModel


class CreateUpdateSubView(CreateUpdateView):
    model = CreateUpdateModel
    fields = ["text_field"]
    success_url = "/"


def test_it_loads_when_GETting_it_with_no_pk(rf):
    """
    Tests a GET using CreateUpdateView with no pk in the request.

    It should return an empty response or empty form.
    """
    # Arrange
    request = rf.get("")

    # Act
    response = CreateUpdateSubView.as_view()(request)

    # Assert
    assert response.status_code == 200


@pytest.mark.django_db
def test_it_loads_when_GETting_it_with_a_pk(rf):
    """
    Tests a GET using CreateUpdateView with a pk in the request.

    It should return the object with the given pk in the response.
    """
    # Arrange
    CreateUpdateModel.objects.create(text_field="test")
    db_object = CreateUpdateModel.objects.first()
    request = rf.get("")

    # Act
    response = CreateUpdateSubView.as_view()(request, pk=db_object.pk)

    # Retrieve
    response_object = response.context_data.get("view").get_object()

    # Assert
    assert response.status_code == 200
    assert response_object == db_object


@pytest.mark.django_db
def test_it_creates_an_object_when_POSTing_with_no_pk(rf):
    """
    Tests a POST using CreateUpdateView with form data
    but no pk in the request.

    It should create a new object with the submitted form data.
    """
    # Arrange
    request = rf.post("", data={"text_field": "test"})

    # Act
    CreateUpdateSubView.as_view()(request)

    # Assert
    assert CreateUpdateModel.objects.count() == 1
    assert CreateUpdateModel.objects.first().text_field == "test"


@pytest.mark.django_db
def test_it_updates_object_when_POSTing_with_a_valid_pk(rf):
    """
    Tests a POST using CreateUpdateView with form data
    and a pk in the request.

    It should update the object with the given pk with the submitted form data.
    """
    # Arrange
    object = CreateUpdateModel.objects.create(text_field="test")
    request = rf.post("", data={"text_field": "changed"})

    # Act
    CreateUpdateSubView.as_view()(request, pk=object.pk)

    # Retrieve
    object.refresh_from_db()

    # Assert
    assert object.text_field == "changed"


@pytest.mark.django_db
def test_it_returns_a_404_when_GETing_it_with_an_invalid_pk(rf):
    """
    Tests a GET using CreateUpdateView with a invalid pk in the request.

    It should return a 404.
    """
    # Arrange
    object = CreateUpdateModel.objects.create(text_field="test")
    request = rf.get("")

    # Act
    with pytest.raises(Http404):
        CreateUpdateSubView.as_view()(request, pk=object.pk + 1)
