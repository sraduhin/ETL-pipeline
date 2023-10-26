import psycopg2
from movies.management.utils.consts import DB_CONNECT
from movies.management.utils.functs import randomize_column_date


def randomize_date(table: str, column: str, db_conn: dict = DB_CONNECT):
    with psycopg2.connect(**db_conn) as postgres_conn:
        cursor = postgres_conn.cursor()
        randomize_column_date(cursor, table, column)
