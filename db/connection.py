from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import os
from contextlib import contextmanager
from functools import cache
from pathlib import Path

load_dotenv()

psql_str = os.getenv("DATABASE_URL")
min_size = os.getenv("min_size", 1)
max_size = os.getenv("max_size", 30)

QUERIES_DIR = Path(__file__).parent / "queries"

pool = ConnectionPool(
    psql_str,
    min_size = min_size,
    max_size = max_size,
    open=True
)

@contextmanager
def get_cursor():
    with pool.connection() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                yield cur

@cache
def load_query(name: str) -> str:
    return (QUERIES_DIR / f"{name}.sql").read_text()

def run_query(name: str, params: tuple = ()):
    sql = load_query(name)
    with get_cursor() as cur:
        cur.execute(sql, params)
        if cur.description is None:
            return None
        return cur.fetchall()
