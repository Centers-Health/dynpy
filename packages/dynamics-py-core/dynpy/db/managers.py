from django.db import models
from dynpy.db.querysets import SoftDeleteQuerySet


class SoftDeleteManager(models.Manager):
    """
    Object manager used to override the `objects` property in `SoftDeleteModelMixin`. Filters out all
    soft-deleted records from the queryset.
    """

    def get_queryset(self):
        """Returns a queryset with soft-deleted records filtered out"""
        return SoftDeleteQuerySet(self.model).filter(deleted_at=None)
