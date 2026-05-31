from django.conf import settings
from django.core.mail import EmailMessage
from django.dispatch import Signal, receiver

from dynpy.logger.enums import LogStatus
from dynpy.templatetags.dynpy_tags import get_reversed_absolute_base_url

# signal provides these params:
# sender: Type[LoggingCommand], log_instance: Log, service_name: str, status: LogStatus,
# post_status_to_team: list[str], send_status_watcher_emails: list[str]
logging_command_completed = Signal()


@receiver(logging_command_completed)
def post_command_status_alerts(sender, log_instance, service_name, status, **kwargs):
    if settings.DJANGO_ENV != "prod":
        return

    send_statuses = kwargs.get("send_status_watcher_emails", [LogStatus.WARN, LogStatus.FAIL])
    team_statuses = kwargs.get("post_status_to_team", [LogStatus.WARN, LogStatus.FAIL])

    subject = f"{log_instance.status}: {service_name}"
    stack_trace = str(log_instance.body)[-1000:]

    if status in send_statuses:
        _send_watcher_emails(subject, stack_trace)

    if status in team_statuses:
        _post_to_teams(subject, stack_trace, log_instance)


def _send_watcher_emails(subject, stack_trace):
    from dynpy.logger.models import Watcher

    try:
        to_addresses = list(
            Watcher.objects.exclude(email__isnull=True)
            .exclude(email="")
            .values_list("email", flat=True)
        )

        if to_addresses:
            email_body = (
                f"Command status alert\n\n"
                f"{subject}\n\n"
                f"Stack Trace:\n{stack_trace}"
            )

            email = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=to_addresses,
            )
            email.send()

    except Exception as e:
        print(f"Failed to send command status watcher emails: {e}")


def _post_to_teams(subject, stack_trace, log_instance):
    from dynpy_teams import actions, blocks, post_to_teams_channel

    try:
        if not settings.COMMAND_STATUSES_TEAMS_CONNECTOR_URL:
            return

        body = [
            blocks.text(f"Stack Trace: {stack_trace}"),
        ]

        admin_logs_page = get_reversed_absolute_base_url(
            "admin:logger_log_change",
            object_id=log_instance.id,
        )

        post_to_teams_channel(
            title=subject,
            body_elements=body,
            actions=[
                actions.openurl_action(
                    title="Go to Admin",
                    url=admin_logs_page,
                )
            ],
            request_kwargs={"timeout": 30},
            url=settings.COMMAND_STATUSES_TEAMS_CONNECTOR_URL,
        )

    except Exception as e:
        print(f"Failed to post command status to Teams: {e}")
