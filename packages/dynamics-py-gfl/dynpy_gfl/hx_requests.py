from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from hx_requests.hx_requests import BaseHxRequest
from hx_requests.utils import deserialize


class InfiniteScroll(BaseHxRequest):
    name = "infinite_scroll"
    GET_block = ["items", "freeze_columns_script", "pagination_under_table"]

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
        "total_and_pagination",
        "tabs_container",
        "freeze_columns_script",
        "gfl_frozen_column_styles",
        "quick_filters",
    ]

    def get_triggers(self, **kwargs) -> list[str]:
        return ["filtered"]


class Sort(BaseHxRequest):
    name = "sort"
    GET_block = ["table", "filters", "filter_message"]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filter"] = self.view.filterset
        return context


class IncludeInfiniteScroll(InfiniteScroll):
    name = "include_infinite_scroll"
    GET_block = ["items"]


class IncludeFilter(Filter):
    name = "include_filter"

    def get(self, request: HttpRequest, *args, **kwargs):
        self.GET_template = [
            self.view.table_template,
            self.view.filters_template,
        ]
        self.GET_block = None
        return super().get(request, *args, **kwargs)


class IncludeSort(Sort):
    name = "include_sort"

    def get(self, request: HttpRequest, *args, **kwargs):
        self.GET_template = [
            self.view.table_template,
            self.view.filters_template,
        ]
        self.GET_block = None
        return super().get(request, *args, **kwargs)


class Pagination(BaseHxRequest):
    name = "pagination"
    GET_block = ["total_and_pagination", "table", "pagination_under_table"]


class BaseSidePanel(BaseHxRequest):
    def get_hx_object(self, request):
        object_id = request.GET.get("object_id")
        if object_id:
            model = self.view.filterset._meta.model
            try:
                return model._base_manager.get(pk=object_id)
            except model.DoesNotExist:
                return None

    def get_triggers(self, **kwargs) -> list[str]:
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

    def get_hx_object(self, request):
        """
        If an 'object' was passed in, deserialize it.
        If the object does not exist, return None (this happens when
        the object was deleted as part of the originial request).
        """
        if request.GET.get("object"):
            try:
                return deserialize(request.GET.get("object"))
            except ObjectDoesNotExist:
                return None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.hx_object:
            self.object_from_qs = None
        else:
            try:
                # get the item from the filtersets qs so that it has the prefetched data
                self.object_from_qs = self.view.filterset.qs.get(pk=self.hx_object.pk)
            except self.hx_object._meta.model.DoesNotExist:
                self.object_from_qs = None
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["is_hx_row_refresh"] = True
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

    def get_triggers(self, **kwargs) -> list[str]:
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
    GET_block = ["table", "filters", "filter_message", "no_objects", "total_and_pagination"]


class GflTotal(BaseHxRequest):
    name = "gfl_total"
    GET_template = "dynpy_gfl/includes/total_and_pagination.html"


class FilterCountsHx(BaseHxRequest):
    """
    HX Request to batch-load counts for filter choices (tabs and quick filters).
    """

    name = "filter_counts"

    def get_filters_to_count(self) -> list[str]:
        """Return list of filter names to compute counts for."""
        filters = []
        if self.view.tabs_filter:
            filters.append("tabs_filter")
        if quick_filters := self.view.get_filterset_class().quick_filters:
            filters.extend(quick_filters)
        return filters

    def get_response_html(self, **kwargs) -> str:
        counts = []
        filterset_class = self.view.get_filterset_class()
        # Use request.GET (raw QueryDict) instead of cleaned_data to avoid passing
        # Python objects (like QuerySets) to widget.value_from_datadict which expects strings
        base_data = self.request.GET.copy()
        # Use the filterset's queryset to ensure custom queryset methods are available
        queryset = self.view.filterset.queryset

        for filter_name in self.get_filters_to_count():
            choices = self.view.filterset.form.fields[filter_name].choices
            for value, _label in choices:
                data = base_data.copy()
                data[filter_name] = value
                count = filterset_class(data=data, queryset=queryset, request=self.request).qs.count()
                counts.append((filter_name, value, count))

        response = render_to_string(
            "dynpy_gfl/filter_counts.html", context={"counts": counts}, request=self.request
        )
        return response


class RefreshAllIds(BaseHxRequest):
    name = "refresh_all_ids"
    GET_template = "dynpy_gfl/bulk_checkbox_gfl.html"
    GET_block = "all_ids"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Limit to at most `max_bulk_amount` IDs to avoid performance and UX issues. Our JS does not
        # handle more than `max_bulk_amount` items anyway.
        #
        # We intentionally fetch/select up to `max_bulk_amount + 1` items so we can detect the
        # overflow case and show a "too many items" tooltip. Without this extra one, users could
        # select "all" and assume the action will run on every item, when in reality we are only
        # process up to `max_bulk_amount`.
        context["all_row_ids"] = self.get_all_ids(**kwargs).values_list("pk", flat=True)[
            : self.view.max_bulk_amount + 1
        ]
        return context

    def get_all_ids(self, **kwargs):
        """
        Hook to get the full queryset of IDs for the "select all" checkbox.

        This method provides the IDs used by the header checkbox to select all filtered
        items at once, even when pagination means not all rows are currently rendered.

        Override this method to exclude items that shouldn't be bulk-selectable. This is
        useful when you're conditionally hiding checkboxes for certain rows via the
        `row_checkbox_td` template block - ensure the exclusion logic here matches your
        template logic to keep them in sync.

        Note:
            If the returned queryset exceeds `max_bulk_amount`, the "select all" checkbox
            will be disabled and show a "too many items" tooltip.

        Returns:
            QuerySet: The filtered queryset whose PKs will populate the "select all" list.
        """
        return self.view.filterset.qs


class BaseBulkHxRequest:
    """
    Base mixin for HxRequests that handle bulk operations on selected items.

    Provides standardized methods for parsing the `selected_ids` parameter that is
    sent by BulkCheckboxGFLMixin views. Selected IDs are passed as a comma-separated
    string in either GET or POST parameters.

    Usage:
        Inherit from this mixin along with your desired HxRequest base class.
        Place BaseBulkHxRequest FIRST in the inheritance chain:

            from dynpy_gfl.hx_requests import BaseBulkHxRequest

            class MyBulkActionHx(BaseBulkHxRequest, FormModalHxRequest):
                name = "my_bulk_action"
                model = MyModel  # Optional: enables get_selected_queryset()

                def get_context_data(self, **kwargs):
                    context = super().get_context_data(**kwargs)
                    context["selected_count"] = len(self.selected_ids_list)
                    context["items"] = self.get_selected_queryset()
                    return context

    Properties:
        selected_ids (str): Raw comma-separated string of selected IDs
        selected_ids_list (list[int]): Parsed list of integer IDs

    Methods:
        get_selected_queryset(): Returns queryset filtered to selected IDs.
            Requires `model` attribute to be set on the class.

    Note:
        This is a mixin class - always inherit from it FIRST (leftmost) in MRO
        so its methods are available to other base classes.

    See Also:
        - `dynpy_gfl.views.BulkCheckboxGFLMixin`: View mixin that sends selected_ids
        - `dynpy_gfl.hx_requests.RefreshAllIds`: Fetches all IDs for "select all" feature
    """

    model = None  # Override in subclass for get_selected_queryset()

    @property
    def selected_ids(self) -> str:
        """
        Return selected IDs as a comma-separated string.

        Reads from POST if this is a POST request, otherwise from GET.
        Returns empty string if parameter is not present.
        """
        request_data = self.request.POST if self.is_post_request else self.request.GET
        return request_data.get("selected_ids", "")

    @property
    def selected_ids_list(self) -> list[int]:
        """
        Return selected IDs as a list of integers.

        Filters out empty strings and non-numeric values.
        Returns empty list if no valid IDs.
        """
        if not self.selected_ids:
            return []
        return [int(id_) for id_ in self.selected_ids.split(",") if id_]

    def get_selected_queryset(self):
        """
        Return a queryset of model instances for the selected IDs.

        Requires the `model` class attribute to be set. Override this method
        for custom queryset logic (e.g., adding select_related, prefetch_related).

        Returns:
            QuerySet filtered to selected IDs

        Raises:
            NotImplementedError: If `model` is not set and method is not overridden
        """
        if self.model is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must set `model` attribute or override get_selected_queryset()"
            )
        return self.model.objects.filter(pk__in=self.selected_ids_list)
