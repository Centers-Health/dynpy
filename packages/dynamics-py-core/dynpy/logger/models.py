from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dynpy.logger.enums import LogStatus


class Log(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # django's auto_now is not nullable. handling this in save() method instead
    completed_at = models.DateTimeField(default="auto_now", null=True)

    app_name = models.CharField(max_length=255, default=None)
    body = models.TextField(default="")
    run_as = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=LogStatus.choices, default=LogStatus.PEND)
    service_name = models.CharField(max_length=255, null=True, default="")

    def __str__(self) -> str:
        return super().__str__()

    def save(self, *args, **kwargs):
        if self.completed_at == "auto_now":
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def update(self, body: str, status: str, is_completed: bool):
        self.body = body
        self.status = status
        self.completed_at = None if is_completed is False else "auto_now"
        self.save()


class Watcher(models.Model):
    email = models.EmailField(max_length=255)

    class Meta:
        verbose_name = _("Watcher")
        verbose_name_plural = _("Watchers")

    def __str__(self):
        return self.email
