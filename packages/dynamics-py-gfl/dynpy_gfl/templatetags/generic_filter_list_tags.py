from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from dynpy.templatetags.dynpy_tags import param_replace

from dynpy_gfl import constants
from dynpy_gfl.utils import reverse_asc_desc_order

register = template.Library()


@register.simple_tag(takes_context=True)
def column_header_link(context, sort_hx_name=None, hx_target=None):
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
    is_order_by_column = column_order_by_clauses and set(
        [order_by.expression for order_by in column_order_by_clauses]
    ).issubset(set([order_by.expression for order_by in order_by]))

    order = reverse_asc_desc_order(order) if is_order_by_column else order
    query_string = param_replace(context, order_by=column_name, order=order)

    # set appropriate arrow icon
    arrow = "up" if order == constants.ASC else "down"
    arrow_tag = f'<i class="fa fa-angle-{arrow}" aria-hidden="true"></i>'

    # only display arrow on column that is currently being ordered by
    arrow_or_empty = arrow_tag if is_order_by_column else ""

    if sort_hx_name:
        query_string = param_replace(
            context, hx_request_name=sort_hx_name, order_by=column_name, order=order
        )
        htmxify = f"""hx-boost='true' hx-target='{hx_target or "#gfl_table"}'
        hx-indicator='#table-loader' hx-swap='outerHTML settle:0 show:#gfl_table:top'"""

    return format_html(
        f"""<a {htmxify if sort_hx_name else ""}
        href="?{query_string}">{column.get("label")} {mark_safe(arrow_or_empty)}</a>"""
    )


@register.filter()
def is_selectpicker(field):
    return field.field.widget.attrs.get("class") and "selectpicker" in field.field.widget.attrs.get(
        "class"
    )


@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None
