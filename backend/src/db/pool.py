import os

from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool

load_dotenv("./.env")
DATABASE_URL = os.environ["DATABASE_URL"]
pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False)
