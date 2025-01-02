from django.db import models


class LogStatus(models.TextChoices):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    INFO = "INFO"
    PEND = "PEND"
    TERM = "TERMINATED"
