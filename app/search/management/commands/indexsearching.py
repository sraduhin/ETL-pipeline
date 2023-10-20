import logging
from django.core.management.base import BaseCommand

from search.management.main import Searcher

CHUNK_SIZE = 100

class Command(BaseCommand):
    help = "Create or rebuild initial Index for searching and fill the base"

    def handle(self, *args, **options):
        index_name = options["index"]
        rebuild = options["rebuild"]

        try:
            index = Searcher()
            if rebuild:
                index.delete_index(index_name)
            index.build_index(index_name)
            start_index = 0
            while True:
                chunk = start_index, start_index + CHUNK_SIZE - 1
                data = index.extract(chunk)
                if not data:
                    break
                index.load(index_name, data)
                start_index += CHUNK_SIZE

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
            "-r",
            "--rebuild",
            action="store_true",
            default=False,
            help='Rebuild existing index',
        )
