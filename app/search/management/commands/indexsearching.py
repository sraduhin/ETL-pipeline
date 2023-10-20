import logging
from django.core.management.base import BaseCommand

from search.management.main import Searcher, build_index


class Command(BaseCommand):
    help = "Create initial Index for searching and fill the base"

    def handle(self, *args, **options):
        index_name = options["index"]
        try:
            index = Searcher()
            index.build_index(index_name)
        except Exception as e:
            logging.error(f"ERROR: {e}")

    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            "--index",
            default="movies",
            help='Index name (default="movies")',
        )