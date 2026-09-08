"""Provide shared helpers for asynchronous database repositories."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional

from psycopg.rows import dict_row

from src.db.async_client.pool import pool


class BaseRepository:
    """Class for interacting with the PostgreSQL database."""

    @asynccontextmanager
    async def _cursor(self, row_factory: Any = dict_row) -> AsyncGenerator[Any, None]:
        """Open a cursor with a pooled database connection.

        Args:
            row_factory (Any): Factory used to convert database rows.

        Yields:
            Any: An asynchronous database cursor.

        """
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=row_factory) as cur:
                yield cur

    @asynccontextmanager
    async def _owned_transaction(
        self, model_id: int, user_id: int, row_factory: Any = None
    ) -> AsyncGenerator[Any, None]:
        """Open a transaction after asserting ownership of a model.

        Args:
            model_id (int): Internal identifier of the model.
            user_id (int): Identifier of the user who must own the model.
            row_factory (Any): Factory used to convert database rows.

        Yields:
            Any: An asynchronous database cursor inside the transaction.

        Raises:
            RuntimeError: If the user does not own the model.

        """
        async with pool.connection() as conn:
            await self._assert_model_owner(conn, model_id, user_id)
            async with conn.transaction():
                async with conn.cursor(row_factory=row_factory) as cur:
                    yield cur

    async def _fetch_one(self, query: str, params: Any = ()) -> Any:
        """Execute a query and return its first row, if present.

        Args:
            query (str): SQL query to execute.
            params (Any): Parameters passed to the query.

        Returns:
            Any: The first row, or None when no row was returned.

        """
        async with self._cursor() as cur:
            await cur.execute(query, params)
            return await cur.fetchone()

    async def _fetch_all(self, query: str, params: Any = ()) -> list[Any]:
        """Execute a query and return all rows.

        Args:
            query (str): SQL query to execute.
            params (Any): Parameters passed to the query.

        Returns:
            list[Any]: Rows returned by the query.

        """
        async with self._cursor() as cur:
            await cur.execute(query, params)
            return [row async for row in cur]

    async def _fetch_val(self, query: str, params: Any = ()) -> Any:
        """Execute a query and return the first column of its first row.

        Args:
            query (str): SQL query to execute.
            params (Any): Parameters passed to the query.

        Returns:
            Any: The first column value, or None when no row was returned.

        """
        async with self._cursor(row_factory=None) as cur:
            await cur.execute(query, params)
            row = await cur.fetchone()
            return row[0] if row is not None else None

    async def _execute(self, query: str, params: Any = ()) -> int:
        """Execute a query and return its affected row count.

        Args:
            query (str): SQL query to execute.
            params (Any): Parameters passed to the query.

        Returns:
            int: Number of rows affected by the query.

        """
        async with self._cursor(row_factory=None) as cur:
            await cur.execute(query, params)
            return cur.rowcount

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
            Optional[datetime]: The parsed datetime object, or None if the
                input is None.

        """
        return datetime.fromisoformat(value) if value else None

    async def _assert_model_owner(self, conn: Any, model_id: int, user_id: int) -> None:
        """Raise an error unless the user owns the model.

        Args:
            conn (Any): The active database connection.
            model_id (int): The internal model ID.
            user_id (int): The user id claiming ownership of the model.

        Raises:
            RuntimeError: If the model does not belong to the user.

        """
        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT 1 FROM models
                WHERE id = %s AND user_id = %s""",
                (model_id, user_id),
            )
            if await cur.fetchone() is None:
                raise RuntimeError(f"Model {model_id} not found")

    async def check_user_exists(self, user_id: int) -> bool:
        """Check whether a user id exists in the database.

        Args:
            user_id (int): The user id to check.

        Returns:
            bool: Whether the user id exists.

        """
        return (
            await self._fetch_val("SELECT 1 FROM users WHERE id = %s", (user_id,))
            is not None
        )

    async def clean_collection(self, collection: str) -> None:
        """Truncate an allowlisted database table.

        Args:
            collection (str): The table name to truncate.

        Raises:
            ValueError: If the table is not in the allowlist.

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
