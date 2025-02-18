from itertools import chain

from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Model
from django.db.models.constants import LOOKUP_SEP
from django.forms.models import BaseModelForm, ModelForm, ModelFormMetaclass, ModelFormOptions
from dynpy.utils.objects import get_attribute


class RelatedModelFormOptions(ModelFormOptions):
    def __init__(self, options=None):
        super().__init__(options)
        self.related_form_classes = getattr(options, "related_form_classes", None)
        self.related_formset_classes = getattr(options, "related_formset_classes", None)
        self.use_unique_instance = getattr(options, "use_unique_instance", None)


class MultiRelatedModelFormMetaclass(ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        new_class._meta = RelatedModelFormOptions(getattr(new_class, "Meta", None))
        return new_class


class MultiRelatedModelForm(BaseModelForm, metaclass=MultiRelatedModelFormMetaclass):
    def __init__(
        self, *args, related_form_kwargs: dict = None, related_formset_kwargs: dict = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.related_form_kwargs = related_form_kwargs or {}
        self.related_formset_kwargs = related_formset_kwargs or {}

    @property
    def related_forms(self) -> dict:
        if not hasattr(self, "_related_forms"):
            self.initialize_related_forms()
        return self._related_forms

    @property
    def related_formsets(self) -> dict:
        if not hasattr(self, "_related_formsets"):
            self.initialize_related_formsets()
        return self._related_formsets

    @property
    def related_formsets_flat(self):
        related_formsets = []
        for formset in self.related_formsets.values():
            if isinstance(formset, list):
                related_formsets.extend(formset)
            else:
                related_formsets.append(formset)
        return related_formsets

    def get_related_form_kwargs(self, lookup: str) -> dict:
        kwargs = self.related_form_kwargs.get(lookup, {}).copy()
        kwargs.update({"prefix": lookup})
        # If the fk field is required and the field is not in the main form
        # then the fk form must be filled out.
        main_lookup, field_name = self.rsplit_lookup(lookup)
        main_form = self.get_form(main_lookup)
        if field_name in main_form.fields and getattr(main_form._meta.model, field_name).field.blank:
            kwargs.update({"use_required_attribute": False, "empty_permitted": True})
        if self.is_bound:
            kwargs.update({"data": self.data, "files": self.files})
        return kwargs

    def get_related_formset_kwargs(self, lookup: str, i: int | None = None) -> dict:
        kwargs = self.related_formset_kwargs.get(lookup, {} if i is None else []).copy()
        prefix = lookup
        if isinstance(kwargs, list) and i is not None:
            try:
                kwargs = kwargs[i]
            except IndexError:
                kwargs = {}
            prefix = f"{lookup}-{i}"
        kwargs.update({"prefix": prefix})
        if self.is_bound:
            kwargs.update({"data": self.data, "files": self.files})
        return kwargs

    def initialize_related_forms(self) -> None:
        related_form_classes = self._meta.related_form_classes or {}
        sorted_lookups = self.sorted_lookups(related_form_classes.keys())
        self._related_forms = {}
        for lookup in sorted_lookups:
            form_class = related_form_classes[lookup]
            main_lookup, field_name = self.rsplit_lookup(lookup)
            main_form = self.get_form(main_lookup)
            instance = getattr(main_form.instance, field_name, None)
            if main_form.initial.get(field_name):
                field = main_form.fields.get(field_name)
                initial = main_form.initial.get(field_name)
                instance = field.to_python(initial) if initial is not None else None
            self._related_forms[lookup] = form_class(
                instance=instance, **self.get_related_form_kwargs(lookup)
            )

    def initialize_related_formsets(self) -> None:
        related_formset_classes = self._meta.related_formset_classes or {}
        self._related_formsets = {}
        for lookup, formset_class in related_formset_classes.items():
            # Get instance of the fk model
            fk_form_lookup, _ = self.rsplit_lookup(lookup)
            instance = (
                get_attribute(self.instance, *fk_form_lookup.split(LOOKUP_SEP))
                if fk_form_lookup
                else self.instance
            )
            if isinstance(formset_class, list):
                self._related_formsets[lookup] = []
                formset_classes = formset_class
                for i, formset_class in enumerate(formset_classes):
                    self._related_formsets[lookup].append(
                        formset_class(instance=instance, **self.get_related_formset_kwargs(lookup, i))
                    )
            else:
                self._related_formsets[lookup] = formset_class(
                    instance=instance, **self.get_related_formset_kwargs(lookup)
                )

    def make_fields_optional(self, lookup: str, form: ModelForm):
        """Make fields with related forms not required."""
        fk_form_lookups = self.get_fk_form_lookups(lookup)
        for fk_form_lookup in fk_form_lookups:
            field_name = fk_form_lookup.split(LOOKUP_SEP)[-1]
            field = form.fields.get(field_name)
            if field:
                field.initial_required = field.required
                field.required = False
                field.widget.attrs["required"] = False

    def get_fk_form_lookups(self, lookup: str) -> list[str]:
        """Get fk form lookups."""
        related_form_classes = self._meta.related_form_classes or {}
        if lookup == "":
            return [lookup for lookup in related_form_classes.keys() if LOOKUP_SEP not in lookup]
        return [
            lookup
            for lookup in related_form_classes.keys()
            if lookup.startswith(lookup) and lookup.count(LOOKUP_SEP) == lookup.count(LOOKUP_SEP) + 1
        ]

    def rsplit_lookup(self, lookup: str) -> list[str]:
        """Split the latter part of the lookup."""
        lookup_parts = lookup.rsplit(LOOKUP_SEP, 1)
        if len(lookup_parts) == 1:
            return ["", lookup_parts[0]]
        return lookup_parts

    def get_form(self, lookup: str) -> ModelForm:
        if lookup == "":
            return self
        return self.related_forms[lookup]

    def sorted_lookups(self, lookups: list[str], fk_first: bool = False) -> list[str]:
        return sorted(lookups, key=lambda x: x.count(LOOKUP_SEP), reverse=fk_first)

    def get_unique_instance(self, instance: ModelForm) -> Model | None:
        """
        Attempt to get an instance that matches the unique fields of the form.
        It will only return an instance if there is exactly one match that matches
        all of the unique field values.
        """
        try:
            instance.validate_unique()
        except ValidationError:
            qs = instance.__class__._default_manager.none()
            unique_checks, date_checks = instance._get_unique_checks()
            unique_filter_kwargs, unique_exclude_kwargs = self.get_unique_look_up_kwargs(
                instance, unique_checks
            )
            date_filter_kwargs, date_exclude_kwargs = self.get_date_lookup_kwargs(instance, date_checks)
            filter_kwargs = {**unique_filter_kwargs, **date_filter_kwargs}
            exclude_kwargs = {**unique_exclude_kwargs, **date_exclude_kwargs}
            if filter_kwargs:
                qs = instance.__class__._default_manager.filter(**filter_kwargs).exclude(
                    **exclude_kwargs
                )

            if qs.count() == 1:
                return qs.first()

    def get_unique_look_up_kwargs(
        self, instance: Model, unique_checks: list[tuple]
    ) -> tuple[dict, dict]:
        # uses identical logic as Model._perform_unique_checks
        filter_kwargs, exclude_kwargs = {}, {}

        for model_class, unique_check in unique_checks:
            lookup_kwargs = {}
            for field_name in unique_check:
                f = instance._meta.get_field(field_name)
                lookup_value = getattr(instance, f.attname)
                if lookup_value is None or (
                    lookup_value == "" and connection.features.interprets_empty_strings_as_nulls
                ):
                    continue
                if f.primary_key and not instance._state.adding:
                    continue
                lookup_kwargs[str(field_name)] = lookup_value

            if len(unique_check) != len(lookup_kwargs):
                continue

            filter_kwargs.update(lookup_kwargs)

            model_class_pk = instance._get_pk_val(model_class._meta)
            if not instance._state.adding and model_class_pk is not None:
                exclude_kwargs["pk"] = model_class_pk

        return filter_kwargs, exclude_kwargs

    def get_date_lookup_kwargs(self, instance: Model, date_checks: list[tuple]) -> tuple[dict, dict]:
        # uses identical logic as Model._perform_date_checks
        filter_kwargs, exclude_kwargs = {}, {}
        for _, lookup_type, field, unique_for in date_checks:
            lookup_kwargs = {}
            date = getattr(instance, unique_for)
            if date is None:
                continue
            if lookup_type == "date":
                lookup_kwargs["%s__day" % unique_for] = date.day
                lookup_kwargs["%s__month" % unique_for] = date.month
                lookup_kwargs["%s__year" % unique_for] = date.year
            else:
                lookup_kwargs["%s__%s" % (unique_for, lookup_type)] = getattr(date, lookup_type)
            lookup_kwargs[field] = getattr(instance, field)

            filter_kwargs.update(lookup_kwargs)

            if not instance._state.adding and instance.pk is not None:
                exclude_kwargs["pk"] = instance.pk

        return filter_kwargs, exclude_kwargs

    def get_unique_form(self, form: ModelForm, lookup: str) -> ModelForm:
        form_class = form.__class__
        form.full_clean()
        unique_instance = self.get_unique_instance(form.instance)
        if unique_instance:
            form = form_class(instance=unique_instance, **self.get_related_form_kwargs(lookup))
        return form

    def is_multipart(self) -> bool:
        return (
            any(
                form.is_multipart()
                for form in chain(self.related_forms.values(), self.related_formsets_flat)
            )
            or super().is_multipart()
        )

    def is_valid(self) -> bool:
        return super().is_valid() and all(
            f.is_valid() for f in chain(self.related_forms.values(), self.related_formsets_flat)
        )

    def has_changed(self) -> bool:
        return (
            any(f.has_changed() for f in chain(self.related_forms.values(), self.related_formsets_flat))
            or super().has_changed()
        )

    def full_clean(self) -> None:
        self.make_fields_optional("", self)
        super().full_clean()
        self.clean_related_forms()
        self.clean_related_formsets()
        if self.is_bound:
            self.validate_required_fields()

    def validate_required_fields(self):
        for lookup, form in self.related_forms.items():
            main_lookup, field_name = self.rsplit_lookup(lookup)
            main_form = self.get_form(main_lookup)
            field = main_form.fields.get(field_name)
            field_is_required = field and field.initial_required
            form_is_empty = not form.cleaned_data
            field_is_empty = not main_form.cleaned_data.get(field_name)
            if all((field_is_required, form_is_empty, field_is_empty)):
                self.add_error(
                    field_name,
                    "Enter a value or fill out the associated form to create a new one.",
                )

    def clean_related_forms(self) -> None:
        if self.is_bound:
            related_form_classes = self._meta.related_form_classes or {}
            use_unique_instance = self._meta.use_unique_instance or []
            sorted_lookups = self.sorted_lookups(related_form_classes.keys())
            for lookup in sorted_lookups:
                main_lookup, field_name = self.rsplit_lookup(lookup)
                main_form = self.get_form(main_lookup)
                form_class = related_form_classes[lookup]
                instance = None
                instance = getattr(main_form.instance, field_name, None)
                form = form_class(instance=instance, **self.get_related_form_kwargs(lookup))
                if lookup in use_unique_instance:
                    form = self.get_unique_form(form, lookup)
                self.make_fields_optional(lookup, form)
                form.full_clean()
                self.related_forms[lookup] = form
        else:
            for form in self.related_forms.values():
                form.full_clean()

    def clean_related_formsets(self) -> None:
        if self.is_bound:
            related_formset_classes = self._meta.related_formset_classes or {}
            sorted_lookups = self.sorted_lookups(related_formset_classes.keys())
            for lookup in sorted_lookups:
                fk_form_lookup, _ = self.rsplit_lookup(lookup)
                fk_form = self.get_form(fk_form_lookup)
                formset_class = related_formset_classes[lookup]
                if isinstance(formset_class, list):
                    self.related_formsets[lookup] = []
                    formset_classes = formset_class
                    for i, formset_class in enumerate(formset_classes):
                        formset = formset_class(
                            instance=fk_form.instance, **self.get_related_formset_kwargs(lookup, i)
                        )
                        formset.full_clean()
                        self.related_formsets[lookup].append(formset)
                else:
                    formset = formset_class(
                        instance=fk_form.instance, **self.get_related_formset_kwargs(lookup)
                    )
                    formset.full_clean()
                    self.related_formsets[lookup] = formset
        else:
            for formset in self.related_formsets_flat:
                formset.full_clean()

    def save_related_forms(self, commit=True) -> None:
        related_form_classes = self._meta.related_form_classes or {}
        sorted_lookups = self.sorted_lookups(related_form_classes.keys(), fk_first=True)
        for lookup in sorted_lookups:
            form = self.related_forms[lookup]
            if not form.has_changed():
                continue
            instance = form.save(commit=commit)
            main_lookup, field_name = self.rsplit_lookup(lookup)
            main_form = self.get_form(main_lookup)
            setattr(main_form.instance, field_name, instance)

    def save_related_formsets(self, commit=True) -> None:
        for formset in self.related_formsets_flat:
            formset.save(commit=commit)

    def save(self, commit=True):
        self.save_related_forms(commit=commit)
        instance = super().save(commit=commit)
        self.save_related_formsets(commit=commit)
        return instance
