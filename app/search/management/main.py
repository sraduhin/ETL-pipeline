import json
import os.path
from datetime import datetime

from elasticsearch import helpers
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, F, functions as f

from movies.models import Filmwork, RoleType
from search.management.schemas import SearchMovie


class State(object):

    @classmethod
    def get_state(cls):
        if os.path.exists(settings.SEARCH_CASH_FILEPATH):
            with open(settings.SEARCH_CASH_FILEPATH, "r") as f:
                return datetime.strptime(
                    json.load(f)["datetime"], settings.SEARCH_CASH_TIME_FORMAT
                )

    @classmethod
    def set_state(cls, dt: datetime):
        with open(settings.SEARCH_CASH_FILEPATH, "w") as f:
            json.dump(
                {"datetime": dt.strftime(settings.SEARCH_CASH_TIME_FORMAT)}, f
            )

    @classmethod
    def clear_state(cls):
        os.remove(settings.SEARCH_CASH_FILEPATH)


class Index(object):
    model = Filmwork

    @staticmethod
    def build(client, index_name: str):
        client.indices.create(index=index_name, **settings.SEARCH_MAPPING)
        print(f"Index name: '{index_name}' has been created")

    @staticmethod
    def delete(client, index_name):
        client.indices.delete(index=index_name)
        print(f"Index name: '{index_name}' has been deleted")


class Extract(object):
    model = Filmwork

    def __init__(self, chunk: tuple, state: datetime = None):
        self.chunk = chunk
        self.state = state

    def get_queryset(self):
        query = self.model.objects.values(
                "id",
                "title",
                "description",
                "modified",
            ).annotate(
                imdb_rating=F("rating"),
                genre=ArrayAgg("genres__name", distinct=True),
                director=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role=RoleType.DIRECTOR),
                    distinct=True,
                ),
                actors=ArrayAgg(
                    f.JSONObject(
                        id="persons__id",
                        name="persons__full_name",
                    ),
                    filter=Q(personfilmwork__role=RoleType.ACTOR),
                    distinct=True,
                ),
                writers=ArrayAgg(
                    f.JSONObject(
                        id="persons__id",
                        name="persons__full_name",
                    ),
                    filter=Q(personfilmwork__role=RoleType.WRITER),
                    distinct=True,
                ),
            )
        if self.state:
            return query.filter(
                modified__gt=self.state
            ).order_by("modified")
        return query.order_by("modified")

    def get_data(self):
        start, end = self.chunk
        return self.get_queryset()[start:end]


class Transform(object):

    @staticmethod
    def get_bulk(index_name: str, data: list[SearchMovie]):
        bulk_data = [
            {
                "_index": index_name,
                "_op_type": "create",
                "_id": str(_["id"]),
                "_source": SearchMovie.transform(_),
            }
            for _ in data
        ]
        return bulk_data


class Load(object):

    @staticmethod
    def load(client, data):
        resp = helpers.bulk(client=client, actions=data)
        print(f"{resp[0]} documents has been loaded.")

