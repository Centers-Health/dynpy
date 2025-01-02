import os
import tempfile
from abc import ABC
from functools import cached_property
from pathlib import Path
from typing import Iterable

from django.http import FileResponse, JsonResponse

from dynpy_gfl.excel.worksheets import WorksheetManager


class Exporter(ABC):
    MAX_RECORDS: int = 4000
    filename: str

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    def export(self) -> FileResponse | JsonResponse:
        if self.get_row_count() > self.MAX_RECORDS:
            return self._too_many_records_response

        with tempfile.TemporaryDirectory() as tmp:
            import pandas as pd  # import here to reduce startup times

            dataframe = pd.DataFrame(self._rows)
            path = os.path.join(tmp, f"{self.get_filename()}.xlsx")
            writer = pd.ExcelWriter(path, engine="openpyxl")
            dataframe.to_excel(writer, sheet_name="Sheet1", index=False)
            workbook = writer.book
            ws = writer.sheets["Sheet1"]
            self._worksheet_manager = WorksheetManager(ws)
            self.set_conditional_formatting()
            workbook.save(path)
            writer.close()

            return FileResponse(
                Path(path).open("rb"), content_type="application/octet-stream"
            )  # noqa: SIM115

    @property
    def _too_many_records_response(self):
        msg = f"The selection size is too big, please filter it down to under {self.MAX_RECORDS} records"
        return JsonResponse({"error_message": msg}, status=401)

    def get_row_count(self) -> int:
        """
        By default, return the length of self._items. If self.get_rows is overridden, then return the
        length of that, since it might not call self.get_items.
        Can override this method if there is a more performant way of getting the row count (e.g.
        queryset.count())
        """
        if type(self).get_rows == Exporter.get_rows:
            return len(self._items)
        else:
            return len(self._rows)

    @cached_property
    def _rows(self):
        """
        Allows self.get_rows to be redefined without interfering with caching
        """
        return self.get_rows()

    def get_rows(self) -> list[dict]:
        return [self.get_row(item=item) for item in self._items]

    @cached_property
    def _items(self):
        """
        Allows self.get_items to be redefined without interfering with caching
        """
        return self.get_items()

    def get_items(self) -> Iterable:
        return []

    def get_row(self, item) -> dict:
        return {}

    def set_conditional_formatting(self):
        return

    def get_filename(self):
        return self.filename


class GFLActionExporter(Exporter):
    def __init__(self, request, view, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.request = request
        self.view = view

    def get_row_count(self) -> int:
        return self.view.filterset.qs.count()

    def get_items(self) -> Iterable:
        return self.view.filterset.qs
