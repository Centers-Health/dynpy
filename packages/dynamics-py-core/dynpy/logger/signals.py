from django.conf import settings
from django.core.mail import EmailMessage
from django.dispatch import Signal, receiver

from dynpy.logger.enums import LogStatus

# signal provides these params:
# sender: Type[LoggingCommand], log_instance: Log, service_name: str, status: LogStatus,
# post_status_to_team: bool, send_status_watcher_emails: bool
logging_command_completed = Signal()


@receiver(logging_command_completed)
def send_status_watcher_emails(sender, log_instance, service_name, status, **kwargs):
    if not kwargs.get("send_status_watcher_emails", True):
        return

    if status not in [LogStatus.FAIL, LogStatus.WARN]:
        return

    from dynpy.logger.models import Watcher

    to_addresses = list(
        Watcher.objects.exclude(email__isnull=True).exclude(email="").values_list("email", flat=True)
    )
    if not to_addresses:
        return

    if status == LogStatus.WARN:
        subject = f"Job Finished with Status of WARN: {service_name}"
    else:
        subject = f"Failed Job: {service_name}"

    stack_trace = str(log_instance.body)[-1000:] if log_instance else ""
    email_body = f"Stack Trace: {stack_trace}"

    try:
        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_addresses,
        )
        email.send()
    except Exception as e:
        print(f"Failed to send command status watcher emails: {e}")
