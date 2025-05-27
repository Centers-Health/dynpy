from enum import Enum

from django.db import models


class FilterListOrder(Enum):
    """
    Used to set the default sort order on a GenericFilterSet
    """

    ASC = "Ascending"
    DESC = "Descending"


class NumberFormat(models.TextChoices):
    INT = "Integer"
    DOLLARS_ONLY = "Dollars Only"


class ListViewStyle(models.TextChoices):
    TABLE = "TABLE"
    CARDS = "CARDS"
