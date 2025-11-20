from django.db import models
from django.utils import timezone
from dynpy.db.managers import SoftDeleteManager


class SoftDeleteModelMixin(models.Model):
    """
    Mixin to make a model soft-deleteable
    """

    # datetime when the record was soft-deleted
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    # Object manager for all records, including soft-deleted. Uses Django's default object manager
    all_objects = models.Manager()

    # Object manager for records that have not been soft-deleted
    objects = SoftDeleteManager()

    class Meta:
        abstract = True
        default_manager_name = "objects"

    def delete(self):
        """
        Soft-deletes the record by setting the `deleted_at` property on to now.

        Returns a tuple containing:

        - total of all records soft-deleted
        - a `dict` with a count of records soft-deleted per model

        (The same as Django's built-in `delete()` method)

        Does not affect any children or parents of the queried records.
        """
        self.deleted_at = timezone.now()
        self.save()
        return (1, {self._meta.model._meta.label: 1})

    def destroy(self):
        """
        Hard-deletes the record by calling Django's built-in `delete()` method.
        """
        return super().delete()

    def undelete(self):
        """Undeletes the record (reverts the deleted_at field to None)"""
        if self.deleted_at is not None:
            self.deleted_at = None
            self.save()
        else:
            raise Exception("Cannot undelete - this record was never deleted.")


class TimestampedModelMixin(models.Model):
    """
    Mixin to add `created_at` and `updated_at` fields to a model
    """

    updated_at = models.DateTimeField(auto_now=True, null=True)
    """datetime when the record was last updated"""
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    """datetime when the record was created"""

    class Meta:
        abstract = True


class ActiveRecordModelMixin(TimestampedModelMixin, SoftDeleteModelMixin):
    class Meta:
        abstract = True
