from decimal import Decimal

from django.db import models


class DecimalValueModel(models.Model):
    value = models.DecimalField(decimal_places=2, max_digits=9, default=Decimal("0.00"))

    class Meta:
        verbose_name = "Decimal Value"
        verbose_name_plural = "Decimal Values"

    def __str__(self) -> str:
        return super().__str__()
