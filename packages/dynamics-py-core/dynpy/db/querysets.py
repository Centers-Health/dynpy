from django.db.models.query import QuerySet
from django.utils import timezone


class SoftDeleteQuerySet(QuerySet):
    """Queryset that can be either soft-deleted or hard-deleted"""

    def delete(self):
        """
        Soft-deletes the queryset by setting the `deleted_at` property on each record to now.

        Returns a tuple containing:

        - total of all records soft-deleted
        - a `dict` with a count of records soft-deleted per model

        (The same as Django's built-in `delete()` method)

        Does not affect any children or parents of the queried records.
        """
        deleted_count = 0
        deleted_count_by_model = {}
        for obj in self:
            obj.deleted_at = timezone.now()
            obj.save()
            deleted_count += 1
            model_label = obj._meta.model._meta.label
            if model_label not in deleted_count_by_model:
                deleted_count_by_model.update({model_label: 0})
            deleted_count_by_model[model_label] += 1
        return (deleted_count, deleted_count_by_model)

    def destroy(self):
        """
        Hard-deletes the queryset by calling Django's built-in `delete()` method.
        """
        return super().delete()
