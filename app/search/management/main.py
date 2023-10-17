from django.contrib.postgres.aggregates import ArrayAgg
from elasticsearch import Elasticsearch

from search.management.utils.consts import MAPPING
from movies.models import Filmwork, RoleType


class Searcher(object):
    model = Filmwork

    def __init__(self):
        self.es = Elasticsearch("http://localhost:9200")

    def get_queryset(self):
        return self.model.objects.select_related().values(
            "id",
            "rating",
            "title",
            "description"
        ).annotate(genres=ArrayAgg('genres__name', distinct=True)).filter(
            personfilmwork__role=RoleType.ACTOR
        ).annotate(
            actors=ArrayAgg('persons__full_name', distinct=True),
        ).filter(
            personfilmwork__role=RoleType.DIRECTOR
        ).annotate(
            directors=ArrayAgg('persons__full_name', distinct=True),
        ).filter(
            personfilmwork__role=RoleType.WRITER
        ).annotate(
            writers=ArrayAgg('persons__full_name', distinct=True),
        )

    def build_index(self, index_name):
        self.es.indices.create(index=index_name)
        resp = self.es.index(index=index_name, document=MAPPING)
        print(f"Index name: \'{index_name}\'. Status: {resp['result']}")

    def extract(self):
        data = self.get_queryset()
        return data

    def transform(self, data):
        transrorm_data = {
            'id': data['id'],
            'title': data['title'],
            'imdb_rating': data['rating'],
            'description': data['description'],
            'writers': data['writers']
        }
        return transrorm_data

    def load(self, index_name):
        data = self.extract()
        for db_movie in data:
            index_movie = self.transform(db_movie)
            self.es.create(index=index_name, id=index_movie['id'], document=index_movie)

    def delete_index(self, index_name):
        resp = self.es.indices.delete(index=index_name)
        print(f"Index name: \'{index_name}\'. Status: \'deleted\'")
