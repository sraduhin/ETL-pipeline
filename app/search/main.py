import json
import os.path
from dataclasses import dataclass, fields
from datetime import datetime

from elasticsearch import helpers
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, F, functions as f

from movies.models import Filmwork, RoleType, Genre, Person
from search.schemas import SearchMovie

@dataclass
class ModelNames():
    FILMWORK: str = "filmwork"
    GENRE: str = "genre"
    PERSON: str = "person"


class State(object):

    @classmethod
    def get_state(cls):
        if os.path.exists(settings.SEARCH_STATE_FILEPATH):
            with open(settings.SEARCH_STATE_FILEPATH, "r") as f:
                state = json.load(f)
                formatted_state = {
                    key: datetime.strptime(
                        value, settings.SEARCH_STATE_TIME_FORMAT
                    )
                    for key, value in state.items()
                    if value is not None
                }
                return formatted_state
        cls.set_default()

    @staticmethod
    def set_default():
        with open(settings.SEARCH_STATE_FILEPATH, "w") as f:
            template = {field.default: None for field in fields(ModelNames)}
            json.dump(template, f)

    @classmethod
    def set_state(cls, **kwargs):
        current_state = cls.get_state()
        with open(settings.SEARCH_STATE_FILEPATH, "w") as f:
            updated_states = {
                key: value.strftime(settings.SEARCH_STATE_TIME_FORMAT)
                for key, value
                in kwargs.items()
                if value is not None
            }
            current_state.update(**updated_states)
            json.dump(current_state, f)


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

    def __init__(self, queryset, chunk: tuple):
        self.queryset = queryset
        self.chunk = chunk

    def get_data(self):
        start, end = self.chunk
        return self.queryset[start:end]


class Context(object):
    filmwork_model = Filmwork

    class Model:
        FILMWORK = Filmwork
        GENRE = Genre
        PERSON = Person

    @staticmethod
    def get_genres(modified: datetime):
        query = (
            Genre.objects.values(
                "id",
            )
            .filter(modified__gt=modified)
            .order_by("modified")
        )
        return query

    @staticmethod
    def get_persons(modified: datetime):
        query = (
            Person.objects.values(
                "id",
            )
            .filter(modified__gt=modified)
            .order_by("modified")
        )
        return query

    @staticmethod
    def get_db_state(model):
        return model.objects.values("id").order_by("modified").last()

    @classmethod
    def get_films(
        cls,
        modified_gt: datetime = None,
        genres: list[Genre] = None, persons: list[Person] = None
    ):
        query = cls._raw_films()
        if modified_gt:
            query = query.filter(modified_gt=modified_gt)
        if genres:
            return query.filter(genres__in=genres).order_by("modified")
        return query.order_by("modified")

    @staticmethod
    def _raw_films():
        return Filmwork.objects.values(
            "id",
            "title",
            "description",
            "modified"
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
