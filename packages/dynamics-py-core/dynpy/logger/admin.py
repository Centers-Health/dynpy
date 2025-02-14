from django.contrib import admin

from .models import Log, Watcher


@admin.register(Log)
class LogsAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = (
        "app_name",
        "service_name",
        "run_as",
        "status",
        "created_at",
        "updated_at",
        "completed_at",
    )
    readonly_fields = (
        "app_name",
        "service_name",
        "run_as",
        "status",
        "created_at",
        "updated_at",
        "completed_at",
        "body",
    )
    search_fields = (
        "app_name",
        "service_name",
        "run_as",
        "status",
        "created_at",
        "updated_at",
        "body",
    )

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


@admin.register(Watcher)
class WatcherAdmin(admin.ModelAdmin):
    pass
