from celery import shared_task
from django.core.management import call_command

@shared_task
def delete_unpaid_orders():
    call_command('delete_unpaid_orders')
