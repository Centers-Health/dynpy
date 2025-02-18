import pytest
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.forms import inlineformset_factory, modelform_factory
from dynpy_forms.forms import MultiRelatedModelForm
from tests.models import Author, Book, Location, Publisher, Tag
from tests.testing_helpers import get_formset_data

pytestmark = pytest.mark.django_db


def test_saves_base_form():
    """Test the model form works without related forms."""

    class AuthorMultiForm(MultiRelatedModelForm):
        class Meta:
            model = Author
            fields = ["name"]

    bound_form = AuthorMultiForm(data={"name": "Bob"})

    assert bound_form.is_valid()
    author = bound_form.save()
    assert author.name == "Bob"


def describe_related_forms():
    def creates_new_instance_through_related_form():
        """Test create parent functionality."""

        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}

        data = {
            "title": "Book 1",
            "author-name": "Bob",
        }
        bound_form = BookMultiForm(data=data)

        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.author.name == "Bob"

    def sets_instance_for_related_forms():
        author = Author.objects.create(name="Bob")
        book = Book.objects.create(title="Book 1", author=author)

        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}

        unbound_form = BookMultiForm(instance=book)

        assert unbound_form.related_forms["author"].instance.pk == book.author.pk

    def sets_instance_for_related_forms_from_initial():
        author = Author.objects.create(name="Bob")
        book = Book.objects.create(title="Book 1", author=author)

        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title", "author"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}

        unbound_form = BookMultiForm(initial={"author": author})

        assert unbound_form.related_forms["author"].instance.pk == book.author.pk

    def updates_instance_through_related_form():
        """Test edit parent functionality."""
        author = Author.objects.create(name="Bob")
        book = Book.objects.create(title="Book 1", author=author)

        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}

        form_data = {
            "title": "Book 1",
            "author": str(author.pk),
            "author-name": "Boby",
        }
        bound_form = BookMultiForm(instance=book, data=form_data)

        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.author.pk == author.pk
        assert book.author.name == "Boby"

    def saves_grandparent_related_forms():
        author = Author.objects.create(name="Bob")

        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title", "publisher", "author"]
                related_form_classes = {
                    "publisher": modelform_factory(Publisher, fields=["name"]),
                    "publisher__location": modelform_factory(Location, fields=["name"]),
                }

        form_data = {
            "title": "Book 1",
            "author": str(author.pk),
            "publisher-name": "Bob",
            "publisher__location-name": "Location 1",
        }
        bound_form = BookMultiForm(data=form_data)

        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.publisher.name == "Bob"
        assert book.publisher.location.name == "Location 1"

    def related_form_updates_instance_from_fk_field_in_parent_form():
        """Test select and edit functionality."""
        author1 = Author.objects.create(name="Bob")
        author2 = Author.objects.create(name="Alice")
        book = Book.objects.create(title="Book 1", author=author1)

        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title", "author"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}

        form_data = {"title": "Book 1", "author": str(author2.pk), "author-name": "Sue"}
        bound_form = BookMultiForm(data=form_data, instance=book)

        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.author.pk == author2.pk
        assert book.author.name == "Sue"

    def related_form_is_not_required_if_model_field_is_not_required():
        publisher = Publisher.objects.create(name="Publisher 1")
        author = Author.objects.create(name="Bob")
        book = Book.objects.create(title="Book 1", publisher=publisher, author=author)

        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title", "author", "publisher"]  # publisher is not required
                related_form_classes = {"publisher": modelform_factory(Publisher, fields=["name"])}

        bound_form = BookMultiForm(instance=book, data={"title": "Book 1", "author": author.pk})

        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.publisher is None

    def model_field_is_not_required_if_related_form_is_filled():
        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title", "author"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}

        bound_form = BookMultiForm(data={"title": "Book 1", "author-name": "Bob"})
        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.author.name == "Bob"

    def adds_custom_field_error_if_model_field_is_required_and_related_form_is_empty():
        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title", "author"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}

        bound_form = BookMultiForm(data={"title": "Book 1"})

        assert not bound_form.is_valid()
        assert bound_form.errors["author"] == [
            "Enter a value or fill out the associated form to create a new one."
        ]

    def related_form_is_required_if_fk_field_is_required_and_not_in_the_form():
        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}

        bound_form = BookMultiForm(data={"title": "Book 1"})

        assert not bound_form.is_valid()
        assert bound_form.related_forms["author"].errors["name"] == ["This field is required."]


def describe_related_formsets():
    def creates_new_instances_through_related_formsets():
        """Test create child set functionality."""

        class AuthorMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Author
                fields = ["name"]
                related_formset_classes = {
                    "book_set": inlineformset_factory(Author, Book, fields=["title"])
                }

        unbound_form = AuthorMultiForm()
        formset = unbound_form.related_formsets["book_set"]
        formset_data = get_formset_data(formset, [{"title": "Book 1"}])
        form_data = {"name": "Bob"}
        bound_form = AuthorMultiForm(data={**form_data, **formset_data})

        assert bound_form.is_valid()
        author = bound_form.save()
        assert author.book_set.count() == 1
        book = author.book_set.first()
        assert book.title == "Book 1"

    def sets_queryset_for_related_formsets():
        author = Author.objects.create(name="Bob")
        Book.objects.create(title="Book 1", author=author)

        class AuthorMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Author
                fields = ["name"]
                related_formset_classes = {
                    "book_set": inlineformset_factory(Author, Book, fields=["title"])
                }

        unbound_form = AuthorMultiForm(instance=author)

        assert list(unbound_form.related_formsets["book_set"].queryset) == list(author.book_set.all())

    def updates_instances_through_related_formsets():
        """Test edit child set functionality."""
        author = Author.objects.create(name="Bob")
        book = Book.objects.create(title="Book 1", author=author)

        class AuthorMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Author
                fields = ["name"]
                related_formset_classes = {
                    "book_set": inlineformset_factory(Author, Book, fields=["title"])
                }

        unbound_form = AuthorMultiForm(instance=author)
        formset = unbound_form.related_formsets["book_set"]
        formset_data = get_formset_data(formset, [{"id": str(book.pk), "title": "Book 2"}])
        form_data = {"name": "Bob"}
        bound_form = AuthorMultiForm(instance=author, data={**form_data, **formset_data})

        assert bound_form.is_valid()
        author = bound_form.save()
        book = author.book_set.first()
        assert book.pk == book.pk
        assert book.title == "Book 2"

    def saves_related_formsets_through_parent_related_form():
        """Test create child set of parent functionality."""

        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title", "author"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}
                related_formset_classes = {
                    "author__tags": generic_inlineformset_factory(Tag, fields=["name"])
                }

        unbound_form = BookMultiForm()

        form_data = {
            "title": "Book 1",
            "author-name": "Bob",
        }
        formset = unbound_form.related_formsets["author__tags"]
        formset_data = get_formset_data(formset, [{"name": "Tag 1"}])
        bound_form = BookMultiForm(data={**form_data, **formset_data})

        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.author.tags.count() == 1
        tag = book.author.tags.first()
        assert tag.name == "Tag 1"

    def related_formset_updates_child_set_from_fk_field_in_parent_form():
        author1 = Author.objects.create(name="Bob")
        author2 = Author.objects.create(name="Alice")
        book = Book.objects.create(title="Book 1", author=author1)

        class BookMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title", "author"]
                related_form_classes = {"author": modelform_factory(Author, fields=["name"])}
                related_formset_classes = {
                    "author__tags": generic_inlineformset_factory(Tag, fields=["name"])
                }

        unbound_form = BookMultiForm()

        form_data = {
            "title": "Book 1",
            "author": str(author2.pk),
            "author-name": "Alice",
        }
        formset = unbound_form.related_formsets["author__tags"]
        formset_data = get_formset_data(formset, [{"name": "Tag 1"}])
        bound_form = BookMultiForm(instance=book, data={**form_data, **formset_data})

        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.author.pk == author2.pk
        tag = book.author.tags.first()
        assert tag.name == "Tag 1"

    def test_handles_multiple_related_formsets_per_lookup():
        """
        Test it can handle multiple related formsets per lookup
        and that formset kwargs accepts a list that passes kwargs to each formset.
        """

        class AuthorMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Author
                fields = ["name"]
                related_formset_classes = {
                    "tags": [
                        generic_inlineformset_factory(Tag, fields=["name", "category"]),
                        generic_inlineformset_factory(Tag, fields=["name", "category"]),
                    ]
                }

        form_kwargs = {
            "related_formset_kwargs": {
                "tags": [{"initial": [{"category": "A"}]}, {"initial": [{"category": "B"}]}]
            }
        }
        unbound_form = AuthorMultiForm(**form_kwargs)
        tag_formsets = unbound_form.related_formsets["tags"]
        form_data_0 = get_formset_data(tag_formsets[0], [{"name": "Tag 1", "category": "A"}])
        form_data_1 = get_formset_data(tag_formsets[1], [{"name": "Tag 2", "category": "B"}])
        bound_form = AuthorMultiForm(**form_kwargs, data={**form_data_0, **form_data_1, "name": "Bob"})
        tag_formsets = bound_form.related_formsets["tags"]

        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.tags.count() == 2
        assert book.tags.filter(category="A", name="Tag 1").exists()
        assert book.tags.filter(category="B", name="Tag 2").exists()


def describe_use_unique_instance():
    """Test get_unique_related functionality."""

    def test_uses_existing_instance_if_name_is_in_use_unique_instance_list():
        # ssn is a unique field
        author = Author.objects.create(name="Bob", ssn="123-45-6789")

        class AuthorMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title"]
                related_form_classes = {
                    "author": modelform_factory(Author, fields=["name", "ssn"]),
                }
                use_unique_instance = ["author"]

        form_data = {"title": "Book 1", "author-name": "Boby", "author-ssn": "123-45-6789"}
        bound_form = AuthorMultiForm(data=form_data)

        assert bound_form.is_valid()
        book = bound_form.save()
        assert book.author.pk == author.pk
        assert book.author.name == "Boby"

    def test_invalid_if_name_is_not_in_use_unique_instance_list():
        Author.objects.create(name="Bob", ssn="123-45-6789")

        class AuthorMultiForm(MultiRelatedModelForm):
            class Meta:
                model = Book
                fields = ["title"]
                related_form_classes = {
                    "author": modelform_factory(Author, fields=["name", "ssn"]),
                }
                use_unique_instance = []

        form_data = {"title": "Book 1", "author-name": "Boby", "author-ssn": "123-45-6789"}
        bound_form = AuthorMultiForm(data=form_data)

        assert not bound_form.is_valid()
        assert "ssn" in bound_form.related_forms["author"].errors
