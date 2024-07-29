from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from order.models import Order


class Command(BaseCommand):
    """Django command to delete unpaid orders older than 3 hours"""

    def handle(self, *args, **kwargs):
        time_threshold = timezone.now() - timedelta(hours=3)
        unpaid_orders = Order.objects.filter(
            is_paid=False,
            created_at__lt=time_threshold,
        )
        count = unpaid_orders.count()
        unpaid_orders.delete()
        self.stdout.write(f"Deleted {count} unpaid orders.")
