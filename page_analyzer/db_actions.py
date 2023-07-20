import os
from typing import Any
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.sql import SQL, Identifier, Placeholder, Composed

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def insert(table_name: str, fields: list[str], values: list[Any]) -> None:

    query = SQL("INSERT INTO %s ({}) VALUES ({})" % table_name).format(
        SQL(', ').join(map(Identifier, fields)),
        SQL(', ').join(Placeholder() * len(fields)))

    with connect(DATABASE_URL) as connection:
        with connection.cursor() as cur:
            cur.execute(query, values)


def select(table_name: str,
           take_all: bool = False,
           fields: list[str] = None,
           where: str = '',
           param: Any = None,
           sort_by='') -> list[tuple]:

    if not take_all:
        query_1 = SQL("SELECT ({}) FROM %s " % table_name).format(
            SQL(', ').join(map(Identifier, fields)))
    else:
        query_1 = SQL("SELECT * FROM %s " % table_name)

    if where:
        query_2 = SQL("WHERE {} = %s ").format(Identifier(where))
    else:
        query_2 = SQL('')

    if sort_by:
        query_3 = SQL("ORDER BY %s DESC" % sort_by)
    else:
        query_3 = SQL('')

    query = Composed([query_1, query_2, query_3, SQL(';')])

    with connect(DATABASE_URL) as connection:
        with connection.cursor() as cur:
            cur.execute(query, [param])
            result = cur.fetchall()
    return result


def select_table_websites() -> list[tuple]:
    with connect(DATABASE_URL) as connection:
        with connection.cursor() as cur:
            cur.execute("""SELECT urls.id, urls.name, 
                                  url_checks.created_at, 
                                  url_checks.status_code 
                           FROM urls LEFT JOIN (SELECT DISTINCT ON 
                                (url_id) url_id, created_at, status_code
                                FROM url_checks
                                ORDER BY url_id, created_at DESC)
                           AS url_checks ON urls.id = url_checks.url_id 
                           ORDER BY urls.id DESC;""")
            result = cur.fetchall()
    return result


def change_structure(data: list[tuple], keys: list[str] = None) -> list[dict]:

    result_list = []

    for tup in data:
        inserted_dict = {}
        zipped = zip(tup, keys)
        for item in zipped:
            inserted_dict.setdefault(item[1], item[0])
        result_list.append(inserted_dict)

    return result_list


def extract_one(data: list[tuple]) -> Any:
    return data[0][0]
