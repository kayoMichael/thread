from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import os
from contextlib import contextmanager

load_dotenv()
psql_str = os.getenv("DATABASE_URL")

pool = ConnectionPool(
    psql_str,
    min_size = 1,
    max_size = 20,
    open=True
)

@contextmanager
def get_cursor():
    with pool.connection() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                yield cur



