import traceback
from typing import Optional

import pyodbc
from django.conf import settings

from dynpy.erroneous.utils import log_erroneous_error


class DatabaseConnector:
    """
    Abstraction for managing a database connection
    """

    database_name: str = "Database"

    def __init__(self, driver, server, username, password, database):
        self._driver: str = driver
        self._server: str = server
        self._username: str = username
        self._password: str = password
        self._database: str = database
        self._conn: Optional[pyodbc.Connection] = None

    def set_conn(self):
        try:
            self._conn = pyodbc.connect(self.connstring)

        except pyodbc.Error as e:
            self.log_connection_error(e)
            raise

    def get_conn(self) -> pyodbc.Connection:
        if self._conn is None:
            self.set_conn()
        return self._conn

    @property
    def connstring(self) -> str:
        return (
            f"DRIVER={self._driver};"
            f"Server={self._server};"
            f"UID={self._username};"
            f"PWD={self._password};"
            f"DATABASE={self._database};"
        )

    def run_sp(self, sp: str, *args, **kwargs) -> pyodbc.Cursor:
        conn = self.get_conn()
        try:
            return conn.cursor().execute(sp, *args)
        except pyodbc.Error as e:
            self.log_connection_error(e)
            raise

    def log_connection_error(self, e: pyodbc.Error):
        log_erroneous_error(
            kind=f"{self.database_name}ConnectionError",
            html=traceback.format_exc(),
            info=f"Error connecting to {self.database_name}.",
            data=str(e),
            path="",
        )


class DWConnector(DatabaseConnector):
    """
    Database connection manager that uses credentials provided in the app settings
    """

    database_name = "DW"

    def __init__(self):
        super().__init__(
            settings.DW_DRIVER,
            settings.DW_SERVER,
            settings.DW_USERNAME,
            settings.DW_PASSWORD,
            settings.DW_DATABASE,
        )


class P1Connector(DatabaseConnector):
    """
    Database connection manager that uses credentials provided in the app settings
    """

    database_name = "P1"

    def __init__(self):
        super().__init__(
            settings.P1_DRIVER,
            settings.P1_SERVER,
            settings.P1_USERNAME,
            settings.P1_PASSWORD,
            settings.P1_DATABASE,
        )
