import logging

from django.core.management.base import BaseCommand
from movies.management.randomizer import randomize_date


class Command(BaseCommand):
    help = "Randomize missing creation date."

    def handle(self, *args, **options):
        db_table = options["table"]
        db_column = options["column"]
        try:
            randomize_date(db_table, db_column)
        except Exception as e:
            logging.error(f"ERROR: {e}")

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--table",
            default="film_work",
            help='required table (default="film_work")',
        )
        parser.add_argument(
            "-c",
            "--column",
            default="creation_date",
            help='required column (default="creation_date")',
        )
