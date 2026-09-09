"""Load shared database configuration from the application environment."""

import os

from dotenv import load_dotenv

load_dotenv("./.env")
DATABASE_URL: str = os.environ["DATABASE_URL"]
