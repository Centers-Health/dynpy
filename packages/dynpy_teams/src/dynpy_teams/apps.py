from django.apps import AppConfig


class DynpyTeamsConfig(AppConfig):
    name = "dynpy_teams"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from dynpy_teams import signals  # noqa: F401
