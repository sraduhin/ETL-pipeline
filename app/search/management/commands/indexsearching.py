import contextlib
import logging

from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch

from search.management.main import Index, State, Transform, Extract, Load
from django.conf import settings


@contextlib.contextmanager
def elasticsearch_conn():
    conn = Elasticsearch(settings.SEARCH_HOST)
    yield conn
    conn.close()


class Command(BaseCommand):
    help = "Create or rebuild initial Index for searching and fill the base"
    CHUNK_SIZE = 89

    def handle(self, *args, **options):
        index_name = options["index"]
        rebuild = options["rebuild"]

        try:
            with elasticsearch_conn() as client:
                if rebuild:
                    Index.delete(client, index_name)
                Index.build(client, index_name)

                start_index = 0
                current_state = State.get_state()

                while True:
                    chunk = start_index, start_index + self.CHUNK_SIZE

                    extractor = Extract(chunk=chunk, state=current_state)
                    db_data = extractor.get_data()
                    if not db_data:
                        break

                    transformer = Transform()
                    search_data = transformer.get_bulk(index_name, db_data)

                    loader = Load()
                    loader.load(client, search_data)
                    if len(db_data) < self.CHUNK_SIZE:
                        break

                    State.set_state(db_data[self.CHUNK_SIZE - 1]["modified"])
                    start_index += self.CHUNK_SIZE

                print("All documents are loaded.")
                State.clear_state()

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
