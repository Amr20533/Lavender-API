from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from community.models import Status

class Command(BaseCommand):
    help = "Delete statuses older than 24 hours"

    def handle(self, *args, **kwargs):
        threshold = timezone.now() - timedelta(hours=24)
        expired = Status.objects.filter(created_at__lt=threshold)
        count = expired.count()
        expired.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} expired statuses."))
