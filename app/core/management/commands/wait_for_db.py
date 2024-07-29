import time
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """Django command to wait for database container to run firstly"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for db...")
        is_db_ready = False

        while is_db_ready is False:
            try:
                self.check(databases=["default"])
                is_db_ready = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write("Database is unavailable, wating for 2 seconds..")
                time.sleep(2)

        self.stdout.write(self.style.SUCCESS("Database is available!"))
