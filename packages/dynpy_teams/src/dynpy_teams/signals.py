from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import get_current_timezone
from dynpy.erroneous.models import Error
from dynpy.logger.enums import LogStatus
from dynpy.logger.signals import logging_command_completed
from dynpy.templatetags.dynpy_tags import get_reversed_absolute_base_url

from . import actions, blocks, post_to_teams_channel


@receiver(post_save, sender=Error)
def post_error_to_teams(sender, instance, created, **kwargs):
    if settings.DJANGO_ENV == "prod" and created and instance.kind.lower() != "js_error":
        try:
            admin_page_url = get_reversed_absolute_base_url(
                "admin:erroneous_error_change", object_id=instance.id
            )
            time = instance.when.astimezone(get_current_timezone()).strftime(
                "On %m/%d/%Y At %-I:%M:%S %p"
            )
            body = [
                blocks.text(f"**{instance.kind}**"),
                blocks.text(""),
                blocks.text(f"Info: {str(instance.info)}"),
                blocks.text(f"Path: {instance.path}"),
                blocks.text(f"Occurred: {time}"),
                blocks.text(f"Stack Trace: {str(instance.data)}"),
            ]

            project_name = getattr(settings, "DYNPY_TEAMS_PROJECT_NAME", "AR")
            post_to_teams_channel(
                title=f"Error in {project_name}",
                body_elements=body,
                actions=[actions.openurl_action(title="Go to admin error page", url=admin_page_url)],
                request_kwargs={"timeout": 10},
                url=settings.DJANGO_ERRONEOUS_TEAMS_CONNECTOR_URL,
            )
        except Exception:
            pass


@receiver(logging_command_completed)
def post_command_status_to_teams(sender, log_instance, service_name, status, **kwargs):
    if settings.DJANGO_ENV == "prod" and status in [LogStatus.FAIL, LogStatus.WARN]:
        try:
            if not settings.COMMAND_STATUSES_TEAMS_CONNECTOR_URL:
                return

            body = [
                blocks.text(f"Stack Trace: {str(log_instance.body)[-1000:]}"),
            ]
            admin_logs_page = get_reversed_absolute_base_url(
                "admin:logger_log_change", object_id=log_instance.id
            )
            post_to_teams_channel(
                title=f"{log_instance.status}: {service_name}",
                body_elements=body,
                actions=[actions.openurl_action(title="Go to Admin", url=admin_logs_page)],
                request_kwargs={"timeout": 30},
                url=settings.COMMAND_STATUSES_TEAMS_CONNECTOR_URL,
            )
        except Exception:
            pass
