import logging
from django.core.management.base import BaseCommand
from search.pipeline import run_pipeline


class Command(BaseCommand):
    help = "Create or rebuild or run Index for searching and fill the base"
    CHUNK_SIZE = 1000

    def handle(self, *args, **options):
        # collect options
        index_name = options["index"]
        rebuild = options["rebuild"]

        try:
            run_pipeline(index_name, rebuild)
        except Exception as e:
            logging.error(f"ERROR: {e}")

    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            "--index",
            default="movies",
            help='Index name (default="movies")',
        )
        parser.add_argument(
            "-b",
            "--rebuild",
            action="store_true",
            default=False,
            help="Rebuild existing index",
        )
