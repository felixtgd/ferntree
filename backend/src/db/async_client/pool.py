"""Create the asynchronous PostgreSQL connection pool."""

from psycopg_pool import AsyncConnectionPool

from src.db.config import DATABASE_URL

# The application lifespan owns opening and closing this shared pool.
pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False)
