import os

import psycopg
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "../.env"))
DATA_TABLES = (
    "models",
    "simulations",
    "sim_timesteps",
    "sim_results_eval",
    "pv_monthly_gen",
    "finances",
    "fin_results",
    "fin_yearly_data",
)


def clean_database() -> None:
    """Truncate backend data tables while preserving reference data."""
    database_url = os.environ["DATABASE_URL"]
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"TRUNCATE TABLE {', '.join(DATA_TABLES)} RESTART IDENTITY CASCADE"
            )
        conn.commit()


if __name__ == "__main__":
    if os.environ.get("CONFIRM_DB_WIPE") != "1":
        raise SystemExit(
            "Refusing to wipe the database. Set CONFIRM_DB_WIPE=1 to continue."
        )
    clean_database()
    print("Backend data tables cleaned; users and loadprofiles were preserved.")
