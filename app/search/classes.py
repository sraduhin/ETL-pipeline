import json
import os.path

import backoff
import elastic_transport

from dataclasses import dataclass, fields
from datetime import datetime

from elasticsearch import helpers
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.db.models import Q, F, functions as f

from movies.models import Filmwork, RoleType, Genre, Person
from search.schemas import SearchMovie


@dataclass
class ModelNames:
    FILMWORK: str = "filmwork"
    GENRE: str = "genre"
    PERSON: str = "person"


class State(object):
    @classmethod
    def get_state(cls):
        if os.path.exists(settings.SEARCH_STATE_FILEPATH):
            state = cls._read_state()
            formatted_state = {
                key: datetime.strptime(value, settings.SEARCH_STATE_TIME_FORMAT)
                if value
                else None
                for key, value in state.items()
            }
            return formatted_state
        cls.set_default()

    @classmethod
    def set_state(cls, **kwargs):
        current_state = cls._read_state()
        with open(settings.SEARCH_STATE_FILEPATH, "w") as f:
            updated_states = {
                key: value.strftime(settings.SEARCH_STATE_TIME_FORMAT)
                for key, value in kwargs.items()
                if value is not None
            }
            current_state.update(**updated_states)
            json.dump(current_state, f)

    @staticmethod
    def set_default():
        with open(settings.SEARCH_STATE_FILEPATH, "w") as f:
            template = {field.default: None for field in fields(ModelNames)}
            json.dump(template, f)

    @staticmethod
    def _read_state():
        with open(settings.SEARCH_STATE_FILEPATH, "r") as f:
            return json.load(f)


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


class Extract(object):
    @staticmethod
    def _old(chunk, queryset):
        start, end = chunk
        return queryset[start:end]

    @staticmethod
    def get_data(queryset, chunk_size):
        paginator = Paginator(queryset, chunk_size)
        for page in range(1, paginator.num_pages + 1):
            yield paginator.page(page).object_list


class Context(object):
    class Model:
        FILMWORK = Filmwork
        GENRE = Genre
        PERSON = Person

    @classmethod
    def get_queryset(
        cls,
        model,
        modified_gt: datetime = None,
        genres: list[Genre] = None,
        persons: list[Person] = None,
    ):
        if model == cls.Model.FILMWORK:
            queryset = cls._raw_films()
        else:
            queryset = model.objects.values("id", "modified")
        query = Q()
        if genres:
            query.add(Q(genres__in=genres), Q.OR)
        if persons:
            query.add(Q(persons__in=persons), Q.OR)
        if modified_gt:
            query.add(Q(modified__gt=modified_gt), Q.OR)
        return queryset.filter(query).order_by("modified")

    @staticmethod
    def _raw_films():
        return Filmwork.objects.values(
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


class Transform(object):
    @staticmethod
    def get_bulk(index_name: str, data: list[SearchMovie]):
        bulk_data = [
            {
                "_index": index_name,
                "_op_type": "index",
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
