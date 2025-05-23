from typing import Dict

from django.http import HttpRequest, HttpResponse
from hx_requests.hx_requests import BaseHxRequest


class InfiniteScroll(BaseHxRequest):
    name = "infinite_scroll"
    GET_block = ["items", "freeze_columns_script"]

    def get(self, request, *args, **kwargs):
        self.view.kwargs["page"] = kwargs.get("page")
        return super().get(request, *args, **kwargs)


class Filter(BaseHxRequest):
    name = "filter"
    GET_block = [
        "table",
        "filters",
        "filter_message",
        "no_objects",
        "total",
        "tabs_container",
        "freeze_columns_script",
        "gfl_frozen_column_styles",
    ]

    def get_triggers(self, **kwargs) -> list:
        return ["filtered"]


class Sort(BaseHxRequest):
    name = "sort"
    GET_block = ["table", "filters"]

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context["filter"] = self.view.filterset
        return context


class SortInline(Sort):
    name = "sort_inline"
    GET_block = ["table", "filters", "filter_message"]


class BaseSidePanel(BaseHxRequest):
    def get_hx_object(self, request):
        object_id = request.GET.get("object_id")
        if object_id:
            model = self.view.filterset._meta.model
            try:
                return model._base_manager.get(pk=object_id)
            except model.DoesNotExist:
                return None

    def get_triggers(self, **kwargs) -> list:
        return ["side_panel_load"]

    def get_response_html(self, **kwargs) -> str:
        """
        Return empty Html if the object does not exist because in that case the side panel should show nothing.
        """
        if not self.hx_object:
            return ""
        return super().get_response_html(**kwargs)


class RefreshRow(BaseHxRequest):
    """
    hx_request triggered by the `refreshRow{item.pk}` (see TriggerRowRefreshMixin).
    Subclass to return the template needed to refresh the row for the page.
    """

    name = "refresh_row"
    GET_block = "table_row_outer"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # get the item from the filtersets qs so that it has the prefetched data
        try:
            self.object_from_qs = self.view.filterset.qs.get(pk=self.hx_object.pk)
        except self.hx_object._meta.model.DoesNotExist:
            self.object_from_qs = None
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context["item"] = self.object_from_qs
        return context

    def get_response_html(self, **kwargs) -> str:
        """
        Return empty Html if the object does not exist in the filterset qs.
        """
        if not self.object_from_qs:
            return ""
        return super().get_response_html(**kwargs)


class TriggerRowRefreshMixin:
    """
    Mixin to be used for hx_requests that need to trigger a refresh of a GFL row on the page.
    Add a kwarg `row_object` to the hx_request and it will trigger a refresh of the row with
    the item's pk.
    """

    def get_triggers(self, **kwargs) -> list:
        triggers = super().get_triggers(**kwargs) or []
        form_valid = self.form.is_valid() if hasattr(self, "form") else True
        if self.is_post_request and kwargs.get("row_object") and form_valid:
            item = kwargs.get("row_object")
            triggers.append(f"refreshRow{item.pk}")
        return triggers


class GflTab(BaseHxRequest):
    """
    This assumes the tab is being processed in the view and filtering down the queryset there.
    """

    name = "gfl_tab"
    GET_block = ["table", "filters", "filter_message", "no_objects", "total"]


class GflTabCounts(BaseHxRequest):
    name = "gfl_tab_counts"

    def _setup_hx_request(self, request, *args, **kwargs):
        # Remove active_tab from the GET params so that it
        # doesn't get passed to the view which would filter down the queryset
        # causing the count to be 0 because it would be filtering by both the tab
        # its doing the count on and the active tab.
        request.GET = request.GET.copy()
        request.GET.pop("active_tab", None)
        super()._setup_hx_request(request, *args, **kwargs)

    def get_response_html(self, **kwargs) -> str:
        tab = self.request.GET.get("tab")
        qs = self.view.filterset.qs
        count = self.view.filter_qs_by_tab(qs, tab).count()
        return str(count)


class GflTotal(BaseHxRequest):
    name = "gfl_total"

    def get_response_html(self, **kwargs) -> str:
        total = self.view.filterset.qs.count()
        return f"{total:,} {self.view.object_name}"
