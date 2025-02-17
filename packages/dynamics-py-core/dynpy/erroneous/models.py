from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _


class Error(models.Model):
    """
    Model for storing the individual errors.
    """

    id = models.AutoField(primary_key=True)

    kind = models.CharField(_("type"), null=False, default="", blank=True, max_length=128, db_index=True)
    info = models.TextField(
        null=False,
    )
    data = models.TextField(blank=True, null=True)
    path = models.TextField(default="")
    when = models.DateTimeField(
        null=False,
        auto_now_add=True,
        db_index=True,
    )
    html = models.TextField(
        null=True,
        blank=True,
    )
    modified = models.DateTimeField(auto_now=True)
    hash = models.TextField()
    count = models.IntegerField(default=1, null=True)

    class Meta:
        """
        Meta information for the model.
        """

        verbose_name = _("Error")
        verbose_name_plural = _("Errors")
        constraints = [UniqueConstraint(name="hash_constraint", fields=["hash"])]

    def __str__(self):
        """
        String representation of the object.
        """
        return f"{self.kind}: {self.info}"
