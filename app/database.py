import psycopg
from app.core.settings import settings
from psycopg.errors import OperationalError

def get_db_connection():
    conn = None
    try:
        conn = psycopg.connect(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
        )
        yield conn

    except OperationalError as e:
        print("Database connection failed:", e)
        raise

    finally:
        if conn is not None:
            conn.close()

