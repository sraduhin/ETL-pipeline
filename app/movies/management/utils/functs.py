import contextlib
import datetime
import logging
import os
import random
import sqlite3
from dataclasses import fields

import psycopg2


@contextlib.contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def is_file_exists(func):
    def wrapper(filepath: str):
        if os.path.exists(filepath):
            return func(filepath)
        logging.error(f"ERROR: '{filepath}' doesn't exist.")

    return wrapper


def get_data_from_sqlite(conn: sqlite3.Connection, table_name: str):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    return cursor.fetchall()


def load_data_to_postgres(
    cursor: psycopg2.extensions.connection.cursor,
    table: str,
    dataclass: object,
    data: list,
):
    col_names = [field.name for field in fields(dataclass)]
    col_count = ", ".join(["%s"] * len(col_names))
    bind_values = ",".join(
        cursor.mogrify(f"({col_count})", row).decode("utf-8") for row in data
    )
    query = f"INSERT INTO content.{table} ({','.join(col_names)}) VALUES {bind_values}"
    cursor.execute(query)


def randomize_column_date(
    cursor: psycopg2.extensions.connection.cursor,
    table: str,
    column: str,
):
    cursor.execute(f"SELECT id from {table}")
    for id in cursor.fetchall():
        today = datetime.date.today()
        random_date = today - datetime.timedelta(days=random.randint(0, 365 * 30))
        query = f"UPDATE {table} SET {column}='{random_date}' WHERE id='{id[0]}'"
        cursor.execute(query)
