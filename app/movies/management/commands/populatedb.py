from django.core.management.base import BaseCommand
from movies.management.transferdb import transfer_db_from_sql_to_postgres


class Command(BaseCommand):
    help = "Populate db from sqlite."

    def handle(self, *args, **options):
        db_path = options["path"]
        transfer_db_from_sql_to_postgres(db_path)

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--path",
            default="db.sqlite",
            help='path to sqlite file (default="./db.sqlite")',
        )
