import os
from typing import Any
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.sql import SQL, Identifier, Placeholder, Composed

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def insert(table_name: str, fields: list[str], values: list[Any]) -> None:
    """
    The function for inserting values into the database by passing table name,
    names of fields to be inserted and their values
    For example:
    insert(table_name='urls',
           fields=['name', 'created_at'],
           values=['example', '11-03-2018'])
    query will be: "INSERT INTO urls (name, created_at)
                        VALUES ('example', '11-03-2018');"
    Then psycopg2 connects to database and insert values
    """

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
    """
    The function retrieves from the database according to the passed parameters,
    while dynamically changing the string if you specify optional arguments.
    A minimal query will require the 'table_name'. Then you need to specify what
    to take from the table by specifying field names in 'fields', or specify
    the 'take_all' param if you need all.

    "table_name" param - table name as string.

    "take_all" param - if True inserts in query symbol '*',
    so you don't need to specify the 'fields' parameter.

    "where" param - field name for which the selection will be performed.

    "param" param - value of the 'where' parameter.

    "sort_by" param - specify the name of the field to be sorted by.
    Sorting always in reverse order.

    Given the optional arguments, the function will create a query string and,
    connecting to the database, execute a sql query. Since the library function
    'fetchall' is used here, the result will always be a list of tuples,
    or in case of no data, just an empty list.
    """

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


def delete(table_name: str, where: str, value: Any) -> None:
    """Deletes a row from a database table"""
    query_1 = SQL('DELETE FROM %s ' % table_name)
    query_2 = SQL('WHERE {} = %s').format(Identifier(where))
    query = Composed([query_1, query_2, SQL(';')])

    with connect(DATABASE_URL) as connection:
        with connection.cursor() as cur:
            cur.execute(query, [value])


def select_table_websites() -> list[tuple]:
    """
    The function executes a large raw sql query using LEFT JOIN. This function
    is fully dedicated to the table with list of all sites on the page.
    """

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
    """
    The function converts the data structure of list of tuples into
    list of dicts. This function is needed only to simplify the data
    structure and for easier use of data in html page templates.
    The main thing is to PASS the KEY NAMES in the CORRECT ORDER.
    """
    result_list = []

    for tup in data:
        inserted_dict = {}
        zipped = zip(tup, keys)
        for item in zipped:
            inserted_dict.setdefault(item[1], item[0])
        result_list.append(inserted_dict)

    return result_list


def extract_one(data: list[tuple]) -> Any:
    """
    This function is written because of the versatility of the 'select' func.
    So, if you got ONLY ONE UNIQUE value after querying the database,
    there is no need to have such a complex structure, this function will
    return that value to you.
    data[0] - first tuple in list, data[0][0] - first item in tuple.
    """
    return data[0][0]
