import datetime
import uuid

from pydantic import BaseModel


class SearchGenre(BaseModel):
    name: str


class SearchPerson(BaseModel):
    id: uuid.UUID
    name: str


class SearchMovie(BaseModel):  # wtf
    id: uuid.UUID
    rating: int
    title: str
    description: str
    modified: datetime.date
    genres: list[SearchGenre]
    directors: list[SearchPerson]
    actors: list[SearchPerson]
    writers: list[SearchPerson]

    @classmethod
    def transform(cls, data):
        return {
            "id": str(data["id"]),
            "imdb_rating": data["imdb_rating"],
            "title": data["title"],
            "description": data["description"],
            "director": data["director"],
            "genre": data["genre"],
            "actors": data["actors"],
            "writers": data["writers"],
            "actors_names": [actor["name"] for actor in data["actors"]],
            "writers_names": [writer["name"] for writer in data["actors"]],
        }
