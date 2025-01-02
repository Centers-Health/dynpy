from django.apps import apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import StateApps
from django.db.models.base import Model


class MigrationTester:
    """
    Utility class for testing data migrations

    Based on https://gist.github.com/blueyed/4fb0a807104551f103e6
    """

    def __init__(self, app, migrate_from, migrate_to) -> None:
        self.executor = MigrationExecutor(connection)
        self.migrate_from = [(app, migrate_from)]
        self.migrate_to = [(app, migrate_to)]
        self.apps = apps

    def migrate_backward(self) -> StateApps:
        self.migrate(self.migrate_from)

    def migrate_forward(self) -> StateApps:
        self.migrate(self.migrate_to)

    def migrate(self, migration) -> StateApps:
        self.executor.migrate(migration)
        self.executor.loader.build_graph()
        self.apps = self.executor.loader.project_state(migration).apps

    def get_current_model(self, app, model) -> Model:
        """
        Get a model at the current db state
        """
        return self.apps.get_model(app, model)
