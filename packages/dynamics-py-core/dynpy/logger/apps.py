from django.apps import AppConfig


class LoggerConfig(AppConfig):
    name = "dynpy.logger"

    def ready(self):
        import dynpy.logger.signals  # noqa: F401
