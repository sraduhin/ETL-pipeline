import contextlib
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from search.main import Context, Extract, Index, Load, State, Transform, ModelNames


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

        # try:
        with elasticsearch_conn() as client:
            if rebuild:
                Index.delete(client, index_name)
                Index.build(client, index_name)
                State.set_default()

            current_state = State.get_state()
            films_state = current_state.get(ModelNames.FILMWORK)

            context = Context.get_films(modified_gt=films_state)

            start_index = 0
            while True:
                chunk = start_index, start_index + self.CHUNK_SIZE

                extractor = Extract(chunk=chunk, queryset=context)
                db_data = extractor.get_data()
                if not db_data:
                    break

                transformer = Transform()
                search_data = transformer.get_bulk(index_name, db_data)

                loader = Load()
                loader.load(client, search_data)

                new_state = db_data[len(db_data) - 1]["modified"]
                State.set_state(**{ModelNames.FILMWORK: new_state})

                if len(db_data) < self.CHUNK_SIZE:
                    break

                start_index += self.CHUNK_SIZE

            print("All documents are loaded.")

        # except Exception as e:
        #     logging.error(f"ERROR: {e}")

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
