from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from dynpy.templatetags.dynpy_tags import param_replace
from dynpy_forms.widgets import MonthPicker
from dynpy_gfl import constants
from dynpy_gfl.utils import reverse_asc_desc_order

register = template.Library()


@register.simple_tag(takes_context=True)
def column_header_link(
    context,
    sort_hx_name=None,
    hx_target="#gfl_table",
    hx_swap="outerHTML settle:0 show:#gfl_table:top",
    hx_indicator="#table-loader",
):
    """
    Returns an anchor tag with the appropriate query string for ordering
    and arrow icon for column headers in generic filter list.
    Keeps ordering consistent across columns
    """
    column = context["column"]
    if not column.get("allow_ordering"):
        return column.get("label")

    # get order_by column from query
    filterset = context["filter"]
    order_by = filterset.qs._query.order_by

    column_name = column.get("field_name")
    column_order_by_clauses = []

    # get order_by from the query if there is no order_by set, use default
    order = constants.DESC if (order_by and order_by[0].descending) else constants.ASC

    # Get to order by for this column, takes order_by_overrides into account
    column_order_by_clauses = filterset.get_order_by([column_name], order)

    # Use `.expression` because the order by contains the order which when being flipped is not the same
    column_order_by_set = {order_by.expression for order_by in column_order_by_clauses}
    order_by_set = {order_by.expression for order_by in order_by}
    is_order_by_column = column_order_by_clauses and column_order_by_set <= order_by_set

    order = reverse_asc_desc_order(order) if is_order_by_column else order
    query_string = param_replace(context, order_by=column_name, order=order)

    # set appropriate arrow icon
    arrow = "up" if order == constants.ASC else "down"
    arrow_tag = f'<i class="fa fa-angle-{arrow}" aria-hidden="true"></i>'

    label = column.get("label")

    # only display arrow on column that is currently being ordered by
    if is_order_by_column:
        arrow_or_empty = arrow_tag
        if label == "__empty_sortable__":
            label = ""
    else:
        if label == "__empty_sortable__":
            # If there is an empty label show something for the user to
            # click on to sort it by. This is opposed to an "" string
            # value which is used to make a non-sortable column
            label = '<i class="fa fa-sort" aria-hidden="true"></i>'
        arrow_or_empty = ""

    if sort_hx_name:
        query_string = param_replace(
            context, hx_request_name=sort_hx_name, order_by=column_name, order=order
        )
        htmxify = f"""hx-boost='true' hx-target='{hx_target}'
        hx-indicator='{hx_indicator}' hx-swap='{hx_swap}'"""

    return format_html(
        f"""<a {htmxify if sort_hx_name else ""}
        href="?{query_string}">{label} {mark_safe(arrow_or_empty)}</a>"""
    )


@register.inclusion_tag("dynpy_gfl/includes/dropdown_sort.html", takes_context=True)
def dropdown_sort(context, sort_hx_name=None, hx_target=None):
    view = context["view"]
    sort_hx_name = sort_hx_name or getattr(view, "sort_hx_name", None)
    hx_target = hx_target or "#gfl_table"
    filterset = context["filter"]
    order_by = filterset.qs._query.order_by
    # get order_by from the query if there is no order_by set, use default
    order = constants.DESC if (order_by and order_by[0].descending) else constants.ASC
    reverse_order = reverse_asc_desc_order(order)
    sort_icon_direction = "down" if order == constants.ASC else "up"

    order_by_column = None

    for column in view.get_columns():
        # Get to order by for this column, takes order_by_overrides into account

        column_order_by_clauses = filterset.get_order_by([column.get("field_name")], order)

        # Use `.expression` because the order by contains the order which when being flipped is not the same
        column_order_by_list = [order_by.expression for order_by in column_order_by_clauses]
        order_by_list = [order_by.expression for order_by in order_by]
        if column_order_by_clauses and column_order_by_list == order_by_list:
            order_by_column = column

    return {
        "order_by_column": order_by_column,
        "order": order,
        "reverse_order": reverse_order,
        "sort_hx_name": sort_hx_name,
        "hx_target": hx_target,
        "sort_icon_direction": sort_icon_direction,
        "request": context["request"],
        "view": view,
    }


@register.filter()
def is_selectpicker(field):
    classes = field.field.widget.attrs.get("class", [])
    return "selectpicker" in classes


@register.filter()
def is_monthpicker(field):
    widget = field.field.widget
    return isinstance(widget, MonthPicker)


@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter
def floor_mid(value):
    return int(value) // 2


@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except ValueError:
        return None
