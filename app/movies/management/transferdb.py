import psycopg2
from movies.management.utils.consts import DB_CONNECT
from movies.management.utils.dataclasses import (FilmWork, Genre,
                                                 GenreFilmWork, Person,
                                                 PersonFilmWork)
from movies.management.utils.functs import (conn_context, get_data_from_sqlite,
                                            is_file_exists,
                                            load_data_to_postgres)

TABLES_WITH_DATACLASSESS = [
    ("genre", Genre),
    ("film_work", FilmWork),
    ("person", Person),
    ("genre_film_work", GenreFilmWork),
    ("person_film_work", PersonFilmWork),
]


@is_file_exists
def transfer_db_from_sql_to_postgres(db_path: str, db_conn: dict = DB_CONNECT):
    with psycopg2.connect(
        **db_conn
    ) as postgres_conn, postgres_conn.cursor() as postgres_curs:
        tables = ["content." + _[0] for _ in TABLES_WITH_DATACLASSESS]
        postgres_curs.execute(f"TRUNCATE {', '.join(tables)}")
        with conn_context(db_path) as sqlite_conn:
            for _ in TABLES_WITH_DATACLASSESS:
                table_name, dataclass = _
                data = get_data_from_sqlite(sqlite_conn, table_name)
                load_data_to_postgres(postgres_curs, table_name, dataclass, data)
