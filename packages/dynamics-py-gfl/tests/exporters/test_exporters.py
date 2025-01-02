import io
from typing import Iterable

import pandas as pd

from dynpy_gfl.excel.exporters import Exporter


class DummyExporter(Exporter):
    filename = "Dummy Export"

    def get_items(self) -> Iterable:
        return ["a", "b"]

    def get_row(self, item) -> dict:
        return {"item": item}


def describe_export():
    def is_xlsx_file():
        response = DummyExporter().export()
        assert response.status_code == 200
        assert "Dummy Export.xlsx" in response.get("Content-Disposition")

    def describe_get_row_count():
        def uses_item_count_by_default():
            exporter = DummyExporter()
            assert exporter.get_row_count() == 2

        def uses_row_count_if_get_rows_is_overridden():
            class ExporterWithCustomGetRows(DummyExporter):
                def get_rows(self) -> Iterable:
                    return [1, 2, 3]

            assert ExporterWithCustomGetRows().get_row_count() == 3

    def rejects_if_too_many_records():
        exporter = DummyExporter()
        exporter.MAX_RECORDS = 0
        response = exporter.export()
        assert response.status_code == 401
        assert "The selection size is too big" in str(response.content)

    def has_one_row_per_item():
        response = DummyExporter().export()
        content = io.BytesIO(response.getvalue())
        dataFrame = pd.read_excel(content)
        assert len(dataFrame.index) == 2

    def works_if_exporter_has_no_data():
        class ExporterWithoutData(DummyExporter):
            def get_items(self) -> Iterable:
                return []

        exporter = ExporterWithoutData()
        exporter.export()
