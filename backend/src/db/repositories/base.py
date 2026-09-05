from datetime import datetime
from typing import Any, Optional

from src.db.pool import pool


class BaseRepository:
    """Class for interacting with the PostgreSQL database."""

    @staticmethod
    def _int_id(value: str) -> Optional[int]:
        """Convert a string ID to an integer ID, or return None if invalid.

        Args:
            value (str): The string ID to convert.

        Returns:
            Optional[int]: The integer ID, or None if the input is invalid.

        """
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """Parse an ISO 8601 datetime string into a datetime object.

        Args:
            value (Optional[str]): The ISO 8601 datetime string to parse.

        Returns:
            Optional[datetime]: The parsed datetime object, or None if the input is
            None.

        """
        return datetime.fromisoformat(value) if value else None

    async def _assert_model_owner(self, conn: Any, model_id: int, user_id: str) -> None:
        """Raise an error unless the user owns the model.

        Args:
            conn (Any): The active database connection.
            model_id (int): The internal model ID.
            user_id (str): The username claiming ownership of the model.

        """
        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT 1 FROM models m JOIN users u ON u.id = m.user_id
                WHERE m.id = %s AND u.username = %s""",
                (model_id, user_id),
            )
            if await cur.fetchone() is None:
                raise RuntimeError(f"Model {model_id} not found")

    async def check_user_exists(self, user_id: str) -> bool:
        """Check whether a username exists in the database.

        Args:
            user_id (str): The username to check.

        Returns:
            bool: Whether the username exists.

        """
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1 FROM users WHERE username = %s", (user_id,))
                return await cur.fetchone() is not None

    async def clean_collection(self, collection: str) -> None:
        """Truncate an allowlisted database table.

        Args:
            collection (str): The table name to truncate.

        """
        allowed = {
            "users",
            "models",
            "simulations",
            "sim_timesteps",
            "sim_results_eval",
            "pv_monthly_gen",
            "finances",
            "fin_results",
            "fin_yearly_data",
            "loadprofiles",
        }
        if collection not in allowed:
            raise ValueError(f"Unknown table: {collection}")
        async with pool.connection() as conn:
            await conn.execute(f"TRUNCATE TABLE {collection} RESTART IDENTITY CASCADE")
