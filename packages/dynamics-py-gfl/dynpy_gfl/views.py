from collections.abc import Sequence
from typing import Any

from django.core.paginator import Paginator
from django.forms import BoundField
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django_filters.filters import Filter
from django_filters.views import FilterView
from dynpy_actions.mixins import ViewActionsMixin
from hx_requests.views import HtmxViewMixin
from render_block import render_block_to_string

from dynpy_gfl.paginators import ComboPaginator, InfiniteScrollPaginator


class GFLIncludeMixin:
    filters_template = "dynpy_gfl/includes/gfl_filters.html"
    filter_hx_name = "include_filter"
    sort_hx_name = "include_sort"
    infinite_scroll_hx_name = "include_infinite_scroll"

    @property
    def table_template(self) -> str:
        raise NotImplementedError(
            "GFLIncludeMixin.table_template must be overridden to provide a template for the table."
        )


class CustomFilterView(FilterView):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.regenerate_filterset_form(context)
        return context

    def regenerate_filterset_form(self, context) -> None:
        """
        Regenerate filterset form fields to give them access to the filtered queryset.
        Only regenerates fields where the parent filter  has `use_filtered_qs_in_field = True`

        Calling self.parent.qs directly from a filter field can result in a stack overflow error (.qs
        checks form.errors, which depends on the filter field, which depends on .qs). However, once
        filterset.qs has been safely called by BaseFilterView's .get() method, it caches the qs on the
        filterset in a ._qs attribute. Since get_context_data is called after that happens, regenerating
        the form fields here allows them to safely check if filterset._qs exists and use it if it does
        (e.g. to check how many records in the filtered qs have a given value).
        """
        filterset = context.get("filter")

        if filterset:

            def delete_cached_filter_field(filter_: Filter) -> None:
                if hasattr(filter_, "_field"):
                    del filter_._field

            def regenerate_form_field(label: str, filter_: Filter) -> None:
                delete_cached_filter_field(filter_)
                filterset.form.fields[label] = filter_.field

            [
                regenerate_form_field(label, filter_)
                for label, filter_ in filterset.filters.items()
                if getattr(filter_, "use_filtered_qs_in_field", False)
            ]


class GenericFilterListView(CustomFilterView):
    """
    Generic filter view with default sortiting, filtering, pagination and template
    that can be overidden for customization.
    Includes an action column for actions related to a row
    """

    template_name = "dynpy_gfl/generic_filter_list.html"
    filterset_class = None
    paginate_by = 50
    paginate_by_options = [10, 25, 50, 100]
    enable_bulk_actions: bool  # not doing as part of ticket
    fixed_header: bool = False
    freeze_columns: int = 0

    def get_columns(self) -> list[dict]:
        """
        A method that returns a list of the column definitions.
        """
        filterset_class = self.get_filterset_class()
        default_fields = filterset_class.Meta.fields

        if isinstance(default_fields, dict):
            default_fields = list(default_fields.keys())

        fields = filterset_class.columns if filterset_class.columns is not None else default_fields
        column_definitions = [
            filterset_class.field_to_column_definition(self, field) for field in fields
        ]
        return column_definitions

    def _get_filters_by_attribute(self, attribute_name: str) -> list[BoundField]:
        """
        Helper method to get filters by filterset attribute name.
        """
        filterset_class = self.get_filterset_class()
        filter_names = getattr(filterset_class, attribute_name, []) or []
        return [field for field in self.filterset.form if field.name in filter_names]

    def get_extra_filters(self) -> list[BoundField]:
        """
        A method that returns a list of extra form filters to be hidden by default.
        """
        return self._get_filters_by_attribute("extra_filters")

    def get_quick_filters(self) -> list[BoundField]:
        """
        A method that returns a list of quick filters to be displayed inline
        and not in the regular filter form.
        """
        return self._get_filters_by_attribute("quick_filters")

    def setup(self, request, *args, **kwargs):
        paginate_by = request.GET.get("paginate_by", None)
        self.filters_collapsed = request.GET.get("filters_collapsed", False)
        if paginate_by:
            self.paginate_by = paginate_by
        return super().setup(request, *args, **kwargs)

    def get_freeze_columns(self) -> int:
        return self.freeze_columns

    @property
    def get_frozen_column_range(self) -> Sequence[int]:
        return range(1, self.get_freeze_columns() + 1)

    @property
    def object_name(self):
        return self.filterset_class.Meta.model._meta.verbose_name_plural.capitalize() or "items"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters_applied_count = (
            len([v for v in self.filterset.form.cleaned_data.values() if v])
            if self.filterset.form.is_valid()
            else 0
        )
        context["filters_applied_count"] = filters_applied_count
        return context


class GflActionsMixin(ViewActionsMixin):
    """
    Mixin for GFLs that adds in ViewActionsMixin and overrides
    the POST to add #{id of row} to the url so that when the page
    reloads the page will jump to the row that was edited by the
    action.
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if (
            request.POST.get("action_name")
            and not request.POST.get("validate")
            and hasattr(response, "url")
            and response.url == request.headers.get("referer", "")
        ):
            return HttpResponseRedirect(response.url + self.get_object_id_anchor(request.POST))
        return response

    def get_object_id_anchor(self, data):
        """
        Pass an anchor to the url of the object_id that was updated
        by the action. This way after the POST on load the page will
        scroll to the row that was just updated by the action.
        """
        if data.get("model_instance_id"):
            return "#" + data.get("model_instance_id")
        return ""


class GenericFilterListWithActionsView(GflActionsMixin, GenericFilterListView):
    pass


class GFLSplitView(GenericFilterListView):
    """
    GFL view with a side panel that can be used to perform tasks
    on the items in the table. All rows are clickable and when
    clicked populate the side panel with the `side_panel_template`.

    The side_panel_template has access to the context along with
    a `split_view_object` which represents the instance of the row that was
    clicked.

    Attributes:
        template_name: Template to be used in the view (make sure to extend
                       `dyn-dynpy_gfl/split_view.html`).
        side_panel_template: Template that is rendered in side panel.
                             Default is a card (can extend it to keep the
                             card layout)
        fixed_header: Sets the table height to fill remainder of the page with
                      fixed headers.
    Usage notes:
        `.js-side-panel-opt-out`
            - Add this class to html elements in a gfl row to prevent the side
                panel from opening when the element is clicked
    """

    template_name = "dynpy_gfl/split_view.html"
    side_panel_template: str = "dynpy_gfl/includes/side_panel.html"
    fixed_header: bool = True
    is_open_by_default = True
    ignore_side_panel_cache = False

    def get(self, request, *args, **kwargs):
        self.object_pk = request.GET.get("split_view_obj", None)
        fetch_side_panel = request.GET.get("fetch_side_panel", None)

        if self.object_pk and fetch_side_panel:
            self.setup_filterset()
            self.paginate_by = None
            context = self.get_context_data(**kwargs)
            return TemplateResponse(request, self.side_panel_template, context)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["split_view_object"] = self.get_object()

        if self.object_pk:
            context.update(**self.get_side_panel_context_data(context["split_view_object"]))

        context["close_side_panel"] = self.is_open_by_default is False and not self.object_pk
        return context

    def setup_filterset(self):
        """
        For the ajax call that loads the side panel to load the
        filterset.
        """
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        self.object_list = self.filterset._meta.model.objects.none()

    def get_object(self):
        model = self.filterset._meta.model
        try:
            return model.objects.get(pk=self.object_pk) if self.object_pk else None
        except model.DoesNotExist:
            return None

    def get_side_panel_context_data(self, split_view_object, **kwargs):
        context = {}
        return context


class GFLSPlitViewWithActions(GflActionsMixin, GFLSplitView):
    pass


class GenericFilterListViewHX(HtmxViewMixin, GenericFilterListView):
    base_gfl_template = "dynpy_gfl/generic_filter_list_htmx.html"
    filter_hx_name = "filter"
    sort_hx_name = "sort"
    infinite_scroll_hx_name = "infinite_scroll"
    row_refresh_hx_name = "refresh_row"
    paginator_class = InfiniteScrollPaginator
    paginator_position_arg = "position"
    include_index_column = False  # If True, the first column will be an index column
    enable_virtual_scroll = False  # If True, the table will use virtual scrolling
    per_combo_page = 100  # The number of items to load per combo page
    show_dropdown_sort = False
    totals_align_right = True

    # Tabs
    has_tabs = False  # If enabled, define filter_qs_by_tab
    tab_hx_name = "gfl_tab"
    tab_counts_hx_name = "gfl_tab_counts"

    @property
    def using_combo_pagination(self):
        return self.paginator_class == ComboPaginator

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if "scrolling" in request.GET:
            context = self.get_context_data()
            return HttpResponse(
                render_block_to_string(self.template_name, "items", context=context, request=request)
            )
        return response

    def get_paginator(
        self,
        queryset,
        per_page,
    ) -> Paginator:
        position = int(self.request.GET.get(self.paginator_position_arg, 0))
        if self.using_combo_pagination:
            combo_page = int(self.request.GET.get("combo_page", 1))
            return self.paginator_class(
                queryset,
                per_page,
                position=position,
                per_combo_page=self.per_combo_page,
                combo_page=combo_page,
            )

        return self.paginator_class(queryset, per_page, position=position)

    def paginate_queryset(self, queryset, page_size):
        """Paginate the queryset, if needed."""
        paginator = self.get_paginator(
            queryset,
            page_size,
        )
        return (paginator, paginator.page, paginator.paginated_object_list, paginator.is_paginated)

    def get_queryset(self):
        # The model is needed for get_queryset and is not set by the FilterView
        self.model = self.get_filterset_class()._meta.model
        qs = super().get_queryset()
        if self.has_tabs:
            tab = self.request.GET.get("active_tab")
            return self.filter_qs_by_tab(qs, tab)
        return qs

    def filter_qs_by_tab(self, qs, tab):
        """
        To be used when tabs are enabled. Override to filter the queryset by the tab.
        Used by default in the GflTabCounts hx-request.
        """
        raise NotImplementedError("filter_qs_by_tab must be implemented when has_tabs is True")


class GFLSplitViewHX(GenericFilterListViewHX):
    base_gfl_template = "dynpy_gfl/split_view_htmx.html"
    side_panel_hx_name = ""
    paginate_by = 20
    default_side_panel_width_percent = 25
    side_panel_is_resizable = True
    side_panel_is_closable = True

    @property
    def default_table_width_percent(self):
        return 100 - self.default_side_panel_width_percent


class GFLCardSplitViewHX(GFLSplitViewHX):
    base_gfl_template = "dynpy_gfl/card_split_view_htmx.html"
    totals_align_right = False
    detail_section_hx_name: str
    show_dropdown_sort = True
    default_side_panel_width_percent = 75
    side_panel_is_resizable = False
    side_panel_is_closable = False

    @property
    def side_panel_hx_name(self):
        """Rename for semantic purposes"""
        return self.detail_section_hx_name


class BulkCheckboxGFLMixin:
    template_name = "dynpy_gfl/bulk_checkbox_gfl.html"
    bulk_action_hx_name = None  # To be set in subclass
    refresh_all_ids_hx_name = "refresh_all_ids"  # HxRequest Must put `all_row_ids` into context
    max_bulk_amount = 10_000  # Max number of items that can be selected for bulk actions

    # Refreshes the table when a bulk action is completed, set on the bulk action HxRequest
    bulk_updated_hx_trigger = "bulk_updated"

    def get(self, request, *args, **kwargs):
        if not self.bulk_action_hx_name:
            raise ValueError("bulk_action_hx_name must be set in subclass")
        return super().get(request, *args, **kwargs)
