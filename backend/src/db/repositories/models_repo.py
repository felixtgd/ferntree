from typing import Any

from psycopg.rows import dict_row

from src.db.models import ModelDataOut
from src.db.pool import pool
from src.db.repositories.base import BaseRepository


class ModelsRepository(BaseRepository):
    """Class for interacting with the PostgreSQL database."""

    async def insert_model(self, model: dict[str, Any]) -> str:
        """Insert a model into the database.

        Args:
            model (dict): The model data to insert.

        Returns:
            str: The string ID of the inserted model.

        """
        coordinates = model.get("coordinates") or {}
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO models (
                        user_id, model_name, location, roof_incl, roof_azimuth,
                        electr_cons, peak_power, battery_cap, time_created,
                        coord_lat, coord_lon, coord_display_name
                    )
                    SELECT id, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    FROM users WHERE username = %s
                    RETURNING id
                    """,
                    (
                        model["model_name"],
                        model["location"],
                        model["roof_incl"],
                        model["roof_azimuth"],
                        model["electr_cons"],
                        model["peak_power"],
                        model["battery_cap"],
                        self._parse_datetime(model.get("time_created")),
                        coordinates.get("lat"),
                        coordinates.get("lon"),
                        coordinates.get("display_name"),
                        model["user_id"],
                    ),
                )
                row = await cur.fetchone()
                if row is None:
                    raise RuntimeError(f"User {model['user_id']} not found")
                return str(row[0])

    @staticmethod
    def _model_from_row(row: dict[str, Any]) -> ModelDataOut:
        coordinates = None
        if row["coord_lat"] is not None:
            coordinates = {
                "lat": row["coord_lat"],
                "lon": row["coord_lon"],
                "display_name": row["coord_display_name"],
            }
        return ModelDataOut(
            user_id=row["username"],
            model_name=row["model_name"],
            location=row["location"],
            roof_incl=row["roof_incl"],
            roof_azimuth=row["roof_azimuth"],
            electr_cons=row["electr_cons"],
            peak_power=row["peak_power"],
            battery_cap=row["battery_cap"],
            coordinates=coordinates,
            time_created=row["time_created"].isoformat()
            if row["time_created"]
            else None,
            model_id=str(row["id"]),
            sim_id=str(row["sim_id"]) if row["sim_id"] is not None else None,
        )

    async def fetch_models(self, user_id: str) -> list[ModelDataOut]:
        """Fetch all models belonging to a user.

        Args:
            user_id (str): The username that owns the models.

        Returns:
            list[ModelDataOut]: The user's models.

        """
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    SELECT m.*, u.username FROM models m
                    JOIN users u ON u.id = m.user_id
                    WHERE u.username = %s ORDER BY m.id
                    """,
                    (user_id,),
                )
                return [self._model_from_row(row) async for row in cur]

    async def fetch_model_by_id(self, model_id: str, user_id: str) -> ModelDataOut:
        """Fetch one user-owned model by its string ID.

        Args:
            model_id (str): The string ID of the model.
            user_id (str): The username that owns the model.

        Returns:
            ModelDataOut: The requested model.

        """
        internal_id = self._int_id(model_id)
        if internal_id is None:
            raise RuntimeError(f"Failed to fetch model with ID {model_id}")
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    SELECT m.*, u.username FROM models m
                    JOIN users u ON u.id = m.user_id
                    WHERE m.id = %s AND u.username = %s
                    """,
                    (internal_id, user_id),
                )
                row = await cur.fetchone()
                if row is None:
                    raise RuntimeError(f"Failed to fetch model with ID {model_id}")
                return self._model_from_row(row)

    async def update_sim_id_of_model(
        self, model_id: str, sim_id: str, user_id: str
    ) -> bool:
        """Associate a simulation with a user-owned model.

        Args:
            model_id (str): The string ID of the model.
            sim_id (str): The string ID of the simulation.
            user_id (str): The username that owns the model.

        Returns:
            bool: Whether the model was updated.

        """
        model_pk, sim_pk = self._int_id(model_id), self._int_id(sim_id)
        if model_pk is None or sim_pk is None:
            return False
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """UPDATE models SET sim_id = %s
                    WHERE id = %s AND user_id = (
                        SELECT id FROM users WHERE username = %s)""",
                    (sim_pk, model_pk, user_id),
                )
                return cur.rowcount > 0

    async def delete_model(self, model_id: str, user_id: str) -> bool:
        """Delete a user-owned model and its dependent records.

        Args:
            model_id (str): The string ID of the model.
            user_id (str): The username that owns the model.

        Returns:
            bool: Whether the model was deleted.

        """
        internal_id = self._int_id(model_id)
        if internal_id is None:
            return False
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """DELETE FROM models WHERE id = %s AND user_id = (
                        SELECT id FROM users WHERE username = %s)""",
                    (internal_id, user_id),
                )
                return cur.rowcount > 0
