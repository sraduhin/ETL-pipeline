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

from movies.models import Filmwork, RoleType, Genre, Person, ModelNames
from search.schemas import SearchMovie


class Storage:
    def __init__(self, filepath):
        self.filepath = filepath

    def retrieve_state(self):
        if os.path.exists(self.filepath):
            state = self._read_state()
            formatted_state = {
                key: datetime.strptime(value, settings.SEARCH_STATE_TIME_FORMAT)
                if value
                else None
                for key, value in state.items()
            }
            return formatted_state
        self.set_default()

    def save_state(self, **kwargs):
        current_state = self._read_state()
        with open(self.filepath, "w") as f:
            updated_states = {
                key: value.strftime(self.filepath)
                for key, value in kwargs.items()
                if value is not None
            }
            current_state.update(**updated_states)
            json.dump(current_state, f)

    def _read_state(self):
        with open(self.filepath, "r") as f:
            return json.load(f)

    def set_default(self):
        with open(self.filepath, "w") as f:
            template = {field.default: None for field in fields(ModelNames)}
            json.dump(template, f)


class State(object):

    def __init__(self, storage):
        self.storage = storage

    def get_state(self):
        return self.storage.retrieve_state()

    def set_state(self, **kwargs):
        self.storage.save_state(**kwargs)
