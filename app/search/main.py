from elasticsearch import Elasticsearch

# from search.utils.consts import MAPPING

# es = Elasticsearch("http://localhost:9200")

MAPPING = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type":       "stop",
                    "stopwords":  "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type":       "stop",
                    "stopwords":  "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "imdb_rating": {
                "type": "float"
            },
            "genre": {
                "type": "keyword"
            },
            "title": {
                "type": "text",
                "analyzer": "ru_en",
                "fields": {
                    "raw": {
                        "type":  "keyword"
                    }
                }
            },
            "description": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "director": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "actors_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "writers_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "actors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "writers": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            }
        }
    }
}


class Indexer(object):

    def __init__(self):
        self.host = "http://localhost:9200"
        self.es = Elasticsearch(self.host)

    def build_index(self):
        resp = self.es.index(index='movies', document=MAPPING)
        print(resp['result'])

    def extract(self):
        pass

    def transform(self):
        pass

    def load(self):
        pass

if __name__ == "__main__":
    indexme = Indexer()
    indexme.build_index()
