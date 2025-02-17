from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Error


@admin.register(Error)
class ErrorAdmin(admin.ModelAdmin):
    list_display = (
        "path_link",
        "kind",
        "info",
        "when",
        "count",
    )
    ordering = ("-id",)
    search_fields = ("path", "kind", "info", "data", "count")
    readonly_fields = (
        "path_link",
        "kind",
        "info",
        "data",
        "when",
        "count",
        "html",
    )
    fieldsets = ((None, {"fields": ("kind", "path_link", "info", "when", "count")}),)

    def path_link(self, obj):
        path = obj.path
        link = reverse("admin:erroneous_error_change", args=(obj.id,))
        # if path is longer than 75 characters, truncate it
        max_length = 75
        path_display_text = path[:max_length] + "..." if len(path) > max_length else path
        return mark_safe(f'<a href="{link}">{path_display_text}</a>')

    change_form_template = "dyn-erroneous/error_change_form.html"

    def has_delete_permission(self, request, obj=None):
        """
        Disabling the delete permissions
        """
        return False

    def has_add_permission(self, request):
        """
        Disabling the create permissions
        """
        return False

    def change_view(self, request, object_id, extra_context=None):
        """
        The detail view of the error record.
        """
        obj = self.get_object(request, object_id)

        if not extra_context:
            extra_context = {}

        if obj:
            extra_context.update(
                {
                    "instance": obj,
                    "error_body": mark_safe(obj.html),
                }
            )

        return super().change_view(request, object_id, extra_context=extra_context)
