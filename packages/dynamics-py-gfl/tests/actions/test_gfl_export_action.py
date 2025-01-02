import io

import pandas as pd
import pytest
from dynpy_actions.utils.testing_utils import handle_action

from dynpy_gfl.actions import GFLExportAction
from dynpy_gfl.excel.exporters import GFLActionExporter
from dynpy_gfl.filtersets import GenericFilterSet
from dynpy_gfl.views import GenericFilterListWithActionsView
from tests.models import DecimalValueModel


class DummyExporter(GFLActionExporter):
    filename = "Dummy Export"

    def get_row(self, item) -> dict:
        return {"pk": item.pk}


class DummyExportAction(GFLExportAction):
    name = "dummy_export_action"
    excel_exporter_class = DummyExporter


class DummyFilterSet(GenericFilterSet):
    class Meta:
        model = DecimalValueModel
        fields = ["value"]


class DummyGFLView(GenericFilterListWithActionsView):
    filterset_class = DummyFilterSet
    actions = [DummyExportAction]


@pytest.fixture()
def test_view(rf, test_user):
    view = DummyGFLView()
    request = rf.get("/")
    request.user = test_user
    view.request = request
    view.kwargs = {}
    return view


def describe_export():
    def is_xlsx_file(test_view):
        action = DummyExportAction()
        action.view = test_view
        response = handle_action(action)
        assert response.status_code == 200
        assert "Dummy Export.xlsx" in response.get("Content-Disposition")

    def applies_filters(test_view):
        DecimalValueModel.objects.bulk_create(
            [
                DecimalValueModel(value=1),
                DecimalValueModel(value=2),
            ]
        )
        action = DummyExportAction()
        action.view = test_view
        response = handle_action(action, request_attrs={"GET": {"value": "1"}})
        content = io.BytesIO(response.getvalue())
        dataFrame = pd.read_excel(content)
        assert len(dataFrame.index) == 1
