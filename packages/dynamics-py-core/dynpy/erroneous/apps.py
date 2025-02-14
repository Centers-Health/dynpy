# flake8: noqa: F401
from django.apps import AppConfig


class ErroneousConfig(AppConfig):
    name = "dynpy.erroneous"

    def ready(self):
        import dynpy.erroneous.signals  # nopycln: import
