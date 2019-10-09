import psycopg2
import psycopg2.pool, psycopg2.extras
from contextlib import contextmanager

from datetime import datetime
from flask import current_app, g

def init_db(app):
    c = app.config
    c['postgreSQL_pool'] = psycopg2.pool.ThreadedConnectionPool(1,20, 
        "dbname=%s user=%s host=%s password=%s" % (c['DB'], c['DB_USER'], c['DB_HOST'], c['DB_PASSWORD']))

    # This function is called at the end of every request
    # It cleans up the database objects. If get_db_and_cursor is used correctly
    # it should not do anything, but it is better to be safe than sorry
    @app.teardown_appcontext
    def close_conn(e):
        cur = g.pop('db_cursor', None)
        if cur is not None:
            print("Reached end of request, but cursor was not closed")
            cursor.close()
        db = g.pop('db', None)
        if db is not None:
            print("Reached end of request, but connection was not returned")
            app.config['postgreSQL_pool'].putconn(db)

@contextmanager
def get_db_and_cursor():
    c = current_app.config
    try: 
        connection = c['postgreSQL_pool'].getconn()
        cursor = connection.cursor()
        g.db = connection
        g.db_cursor = cursor
        yield (connection, cursor)
    finally:
        g.pop('db', None)
        g.pop('db_cursor', None)
        cursor.close()
        c['postgreSQL_pool'].putconn(connection)

