import sys

import backoff
import contextlib

import django.db.utils
import elastic_transport
from django.conf import settings
from elasticsearch import Elasticsearch
from search.classes import (Context, Extract, Index, Load, State, Transform,
                            ModelNames)

CHUNK_SIZE = 1000


def _giveup(e):
    print("\n >>>> Giving up after multiple failures...")
    sys.exit(-1)


def _backoff(details):
    print("\n >>>> Failed connection. Reconnecting...")


@backoff.on_exception(backoff.expo,
                      django.db.utils.OperationalError,
                      on_giveup=_giveup,
                      on_backoff=_backoff,
                      max_tries=5,
                      jitter=backoff.random_jitter,
                      max_time=16,
                      )
@backoff.on_exception(backoff.expo,
                      elastic_transport.ConnectionError,
                      on_giveup=_giveup,
                      on_backoff=_backoff,
                      max_tries=5,
                      jitter=backoff.random_jitter,
                      max_time=16,
                      )
def run_pipeline(index: str, rebuild: bool):

    with Elasticsearch(settings.SEARCH_HOST) as client:
        if rebuild or not Index.is_exists(index, client):
            # building index from zero
            Index.rebuild(index, client)

        # getting the time of last checks
        current_state = State.get_state()
        films_state = current_state.get(ModelNames.FILMWORK)
        genres_state = current_state.get(ModelNames.GENRE)
        persons_state = current_state.get(ModelNames.PERSON)

        # constructing query to get updates
        # from last checks in genres & persons
        genres_diff = Context.get_queryset(
            model=Context.Model.GENRE,
            modified_gt=genres_state
        )
        persons_diff = Context.get_queryset(
            model=Context.Model.PERSON,
            modified_gt=persons_state
        )
        genres_chunks = Extract.get_data(
            queryset=genres_diff, chunk_size=CHUNK_SIZE
        )
        persons_chunks = Extract.get_data(
            queryset=persons_diff, chunk_size=CHUNK_SIZE
        )
        while True:
            # getting updates by chunks
            genres = next(genres_chunks, None)
            persons = next(persons_chunks, None)

            # constructing filter to find filmworks
            fw_filters = {
                "modified_gt": films_state,
                "genres": [
                    genre["id"] for genre in genres
                ] if genres else None,
                "persons": [
                    person["id"] for person in persons
                ] if persons else None,
            }
            # constructing query to get film updates
            films_diff = Context.get_queryset(
                model=Context.Model.FILMWORK, **fw_filters
            )
            films_generator = Extract.get_data(
                queryset=films_diff, chunk_size=CHUNK_SIZE
            )
            while True:
                films = next(films_generator, None)

                if not films:
                    break

                # transforming data according to ES & load
                loading_data = Transform.get_bulk(index, films)
                Load().load(client, loading_data)

                # updating state in FW
                State.set_state(**{
                    ModelNames.FILMWORK: films[len(films) - 1]["modified"]
                })

            if not genres and not persons:
                break
            # updating state in genres & persons
            State.set_state(
                **{
                    ModelNames.GENRE:
                        genres[len(genres) - 1]["modified"]
                        if genres
                        else None,
                    ModelNames.PERSON:
                        persons[len(persons) - 1]["modified"]
                        if persons
                        else None,
                }
            )

        print("All documents are loaded.")
