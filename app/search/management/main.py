import elasticsearch.helpers
from elasticsearch import Elasticsearch, helpers
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, functions as f
from django.db.models.functions import JSONObject

from movies.models import Filmwork, RoleType
from search.management.utils.consts import MAPPING, HOST
from search.management.utils.functs import elasticsearch_client


class Searcher(object):
    model = Filmwork

    def build_index(self, index_name: str):
        with Elasticsearch(HOST) as client:
            client.indices.create(index=index_name, **MAPPING)
            print(f"Index name: \'{index_name}\' has been created")

    def extract(self):
        return self.model.objects.select_related().values(
            "id",
            "rating",
            "title",
            "description"
        ).annotate(
            genre=ArrayAgg('genres__name', distinct=True)
        ).annotate(
            director=ArrayAgg(
                'persons__full_name',
                filter=Q(personfilmwork__role=RoleType.DIRECTOR),
                distinct=True,
            ),
        ).annotate(
            actors=ArrayAgg(
                f.JSONObject(
                    id='persons__id',
                    name='persons__full_name',
                ),
                filter=Q(personfilmwork__role=RoleType.ACTOR),
                distinct=True
            ),
        ).annotate(
            writers=ArrayAgg(
                f.JSONObject(
                    id='persons__id',
                    name='persons__full_name',
                ),
                filter=Q(personfilmwork__role=RoleType.WRITER),
                distinct=True
            ),
        )

    def transform(self, index_name: str, data: list):
        transrorm_data = [
            {
                "_index": index_name,
                "_op_type": "create",
                "_id": str(element['id']),
                "_source": {
                    'id': str(element['id']),
                    'title': element['title'],
                    'imdb_rating': element['rating'],
                    'description': element['description'],
                    'genre': element['genre'],
                    'director': element['director'],
                    'actors': element['actors'],
                    'writers': element['writers'],
                    'actors_names': [
                        actor['name'] for actor in element['actors']
                    ],
                    'writers_names': [
                        writer['name'] for writer in element['writers']
                    ],
                }
            } for element in data
        ]
        return transrorm_data

    def load(self, index_name):
        data = self.extract()
        bulk_data = self.transform(index_name, data)

        with Elasticsearch(HOST) as client:
            resp = helpers.bulk(client=client, actions=bulk_data)
            print(resp)

    def delete_index(self, index_name):
        with Elasticsearch(HOST) as client:
            client.indices.delete(index=index_name)
            print(f"Index name: \'{index_name}\' has been deleted")
