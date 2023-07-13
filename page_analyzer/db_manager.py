from psycopg2 import connect
from datetime import date


def connect_db(token):
    connection = connect(token)
    return connection


def add_url(connection, url):
    with connection.cursor() as cur:
        cur.execute("""
        INSERT INTO urls (name, created_at) VALUES (%s, %s);
        """, [url, date.today()])


def get_by_id(connection, id):
    with connection.cursor() as cur:
        cur.execute(""" SELECT * FROM urls WHERE id = %s; """, [id])
        output = cur.fetchone()
    return {"id": output[0],
            "name": output[1],
            "created_at": output[2]}


def get_id(connection, name):
    with connection.cursor() as cur:
        cur.execute(""" SELECT id FROM urls WHERE name = %s; """, [name])
        url_id = cur.fetchone()
    return url_id[0] if url_id else None


def get_all_data(connection):
    with connection.cursor() as cur:
        cur.execute(""" SELECT * FROM urls ORDER BY id DESC; """)
        all_data = cur.fetchall()

    data_list = []
    for item in all_data:
        data_list.append(
            {"id": item[0],
             "name": item[1],
             "created_at": item[2]})
    return data_list
