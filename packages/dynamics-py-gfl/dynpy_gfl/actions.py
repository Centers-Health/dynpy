from django.http.response import HttpResponse
from dynpy_actions.actions import ViewActions
from dynpy_actions.enums import EmbedType

from dynpy_gfl.excel.exporters import GFLActionExporter
from dynpy_gfl.forms import GFLExportForm


class GFLExportAction(ViewActions):
    """
    An action for exporting a GFL page to an excel file
    """

    element = GFLExportForm
    embed_type = EmbedType.INLINE
    pre_render = True
    excel_exporter_class: GFLActionExporter

    def handle(self, request, form, **kwargs) -> HttpResponse:
        self.request = request
        self.setup_view()
        exporter = self.excel_exporter_class(request, self.view, **self.get_excel_exporter_kwargs())
        response = exporter.export()
        response["HX-Trigger"] = "exported"
        # Set response.url to None since GflActionsMixin expects the response to have url attribute
        response.url = None
        return response

    def setup_view(self):
        self.view.setup(self.request)
        self.view.get(self.request)

    def get_excel_exporter_kwargs(self):
        return {}
