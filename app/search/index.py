from datetime import datetime

from elasticsearch import helpers
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.db.models import Q, F, functions as f

from movies.models import Filmwork, RoleType, Genre, Person
from search.schemas import SearchMovie
from search.state import State


class Index(object):

    @classmethod
    def rebuild(cls, index, client):
        if cls.is_exists(index, client):
            cls._delete(index, client)
        cls._build(index, client)
        State.set_default()

    @staticmethod
    def _build(index, client):
        client.indices.create(index=index, **settings.SEARCH_MAPPING)
        print(f"Index name: '{index}' has been created")

    @staticmethod
    def _delete(index, client):
        client.indices.delete(index=index)
        print(f"Index name: '{index}' has been deleted")

    @staticmethod
    def is_exists(index, client):
        check_index = client.indices.exists(index=index)
        if check_index.body:
            return True
