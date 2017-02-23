import connexion
from connexion import NoContent
from psycopg2 import IntegrityError

from app.db import dbconn
from app.utils import strip_column_prefix, slugger


def get():
    with dbconn() as conn:
        cur = conn.cursor()
        cur.execute('''SELECT pg_name, pg_slug, pg_department FROM zsm_data.product_group''')
        rows = cur.fetchall()
        res = [strip_column_prefix(r._asdict()) for r in rows]
        return res


def add(product_group):
    with dbconn() as conn:
        cur = conn.cursor()
        try:
            cur.execute('''INSERT INTO zsm_data.product_group (pg_name, pg_department, pg_slug) VALUES (%s, %s, %s)''',
                        (product_group['name'], product_group['department'], slugger(product_group['name'])))
            conn.commit()
            cur.close()
            return NoContent, 201
        except IntegrityError:
            return connexion.problem(status=400, title='Product Group already exists',
                                     detail='Product group with name: "{}" already exists!'.format(
                                         product_group['name']))


def delete(pg_slug: str):
    with dbconn() as conn:
        cur = conn.cursor()
        cur.execute('''DELETE FROM zsm_data.product_group WHERE pg_slug = %s''', (pg_slug,))
        conn.commit()
        return (NoContent, 404) if not cur.rowcount else (NoContent, 200)
