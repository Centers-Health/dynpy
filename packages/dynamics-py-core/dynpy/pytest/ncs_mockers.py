from typing import Any


class Cursor:
    """
    Used to mock the cursor object returned from DWConnector.run_sp
    """

    data: Any

    def __init__(self, data) -> None:
        self.data = data

    def __iter__(self):
        for row in self.data:
            yield row

    def fetchall(self):
        return self.data

    @property
    def description(self):
        return [[key] for key in self.data[0].__dict__.keys()]


class NCSRow:
    """
    This class represents a row coming from NCS

    To use: Inherit from this class and set all the row properties in the init function
    """

    def __iter__(self):
        for value in self.__dict__.values():
            yield value

    def get(self, key):
        return getattr(self, key, None)
