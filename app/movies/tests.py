from django.test import TestCase
from movies.management.commands.populatedb import DB_CONNECT
from movies.management.transferdb import (TABLES_WITH_DATACLASSESS,
                                          transfer_db_from_sql_to_postgres)
from movies.management.utils import conn_context

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork

TEST_DB_CONNECT = DB_CONNECT
TEST_DB_CONNECT["dbname"] = "test_movies_database"
SQL_DB = "db.sqlite"

TABLES_WITH_DATACLASSESS = [
    ("genre", Genre),
    ("film_work", Filmwork),
    ("person", Person),
    ("genre_film_work", GenreFilmwork),
    ("person_film_work", PersonFilmwork),
]


# Create your tests here.
class PopulateDBTest(TestCase):
    def setUp(self):
        pass

    def test_count(self):
        transfer_db_from_sql_to_postgres(TEST_DB_CONNECT, "db.sqlite")
        with conn_context(SQL_DB) as sqlite_conn:
            for _ in TABLES_WITH_DATACLASSESS:
                table, obj_class = _
                cursor = sqlite_conn.cursor()
                cursor.execute(f"SELECT id FROM {table};")
                expected = cursor.fetchall()
                expected_set = {row[0] for row in expected}
                result = obj_class.objects.values_list("id", flat=True)
                result_set = {str(row) for row in result}
                self.assertEquals(result_set, expected_set)
