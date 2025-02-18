from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    category = models.CharField(max_length=100)

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "location"
        verbose_name_plural = "locations"

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "publisher"
        verbose_name_plural = "publishers"

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    ssn = models.CharField(max_length=100, unique=True, blank=True, null=True)
    tags = GenericRelation(Tag)

    class Meta:
        verbose_name = "author"
        verbose_name_plural = "authors"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "book"
        verbose_name_plural = "books"

    def __str__(self):
        return self.title
