from elasticsearch import Elasticsearch


def elasticsearch_client(host: str):
    with Elasticsearch(host) as e:
        yield e
