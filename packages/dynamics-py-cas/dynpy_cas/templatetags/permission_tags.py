from django.template import Library, Node
from django.urls import resolve

from dynpy_cas.permission_checks import has_edit_permission, has_global_search_access

register = Library()


class EditorOnlyNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        request = context["request"]
        output = self.nodelist.render(context)
        app_name = resolve(request.path).app_name

        if app_name and has_edit_permission(request.user, app_name) is False:
            return ""

        return output


@register.tag("editor_only")
def do_editor_only(parser, token):
    """
    Hides everything within this block for users that
    do not have edit permission.

    Example usage:
    ```
    {% load permission_tags %}
    {% editor_only %}
        Editor only content
    {% end_editor_only %}
    ```
    """
    nodelist = parser.parse(("end_editor_only",))
    parser.delete_first_token()
    return EditorOnlyNode(nodelist)


@register.filter(name="has_edit_permission")
def do_has_edit_permission(user, app_name) -> bool:
    """
    Returns True if the user has edit permission for the given app_name.

    Example usage:
    ```
    {% load permission_tags %}
    {% if request.user|has_edit_permission:request.resolver_match.app_name %}
        Editor only content
    {% endif %}
    ```
    """
    return has_edit_permission(user, app_name)


register.filter(has_global_search_access)
