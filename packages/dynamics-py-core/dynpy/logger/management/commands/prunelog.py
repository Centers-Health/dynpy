from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone

from dynpy.logger.models import Log


class Command(BaseCommand):
    help = "Clear old logs from the database"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "days",
            type=int,
            nargs="?",
            default=30,
            help="Indicates the number of days of logs that will be kept, including today",
        )

    def handle(self, *args, **options) -> None:
        days = options["days"]
        now = timezone.now()
        midnight_today = timezone.make_aware(datetime(now.year, now.month, now.day, 0, 0, 0))
        # Subtracting 1 to include today in count
        earliest_time_to_keep = midnight_today - timedelta(days=days - 1)
        logs_to_delete = Log.objects.filter(updated_at__lt=earliest_time_to_keep)
        deleted_log_count = logs_to_delete.count()
        logs_to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_log_count} log(s)."))
