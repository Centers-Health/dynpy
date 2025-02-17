from django.db import models
from dynpy.db.model_mixins import ActiveRecordModelMixin, SoftDeleteModelMixin, TimestampedModelMixin


class TestSoftDeleteModel(SoftDeleteModelMixin):
    pass


class TestTimestampedModel(TimestampedModelMixin):
    pass


class TestActiveRecordModel(ActiveRecordModelMixin):
    test_char_field = models.CharField(max_length=255, null=True, blank=True)


class DocumentTestModel(models.Model):
    file = models.FileField()

    def __str__(self) -> str:
        return super().__str__()


class DocumentTestModel2(models.Model):
    document = models.FileField()

    def __str__(self) -> str:
        return super().__str__()


class CreateUpdateModel(models.Model):
    text_field = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return super().__str__()
