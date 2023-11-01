import argparse
import contextlib
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch

from search.classes import (Context, Extract, Index, Load, State, Transform,
                            ModelNames)
from search.pipeline import run_pipeline


@contextlib.contextmanager
def elasticsearch_conn():
    conn = Elasticsearch(settings.SEARCH_HOST)
    yield conn
    conn.close()


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
