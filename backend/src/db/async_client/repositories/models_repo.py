"""Persist and retrieve user-owned models asynchronously."""

from typing import Any

from src.db.async_client.repositories.base import BaseRepository
from src.db.schemas import ModelDataOut


class ModelsRepository(BaseRepository):
    """Class for interacting with the PostgreSQL database."""

    async def insert_model(self, model: dict[str, Any], user_id: int) -> str:
        """Insert a model into the database.

        Args:
            model (dict): The model data to insert.
            user_id (int): The user id that owns the model.

        Returns:
            str: The string ID of the inserted model.

        """
        coordinates = model.get("coordinates") or {}
        model_id = await self._fetch_val(
            """
            INSERT INTO models (
                user_id, model_name, location, roof_incl, roof_azimuth,
                electr_cons, peak_power, battery_cap, time_created,
                coord_lat, coord_lon, coord_display_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                user_id,
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
            ),
        )
        return str(model_id)

    @staticmethod
    def _model_from_row(row: dict[str, Any]) -> ModelDataOut:
        """Convert a database row into a model response.

        Args:
            row (dict[str, Any]): Database row containing model fields.

        Returns:
            ModelDataOut: Model data parsed from the row.

        """
        coordinates = None
        if row["coord_lat"] is not None:
            coordinates = {
                "lat": row["coord_lat"],
                "lon": row["coord_lon"],
                "display_name": row["coord_display_name"],
            }
        return ModelDataOut(
            user_id=row["user_id"],
            model_name=row["model_name"],
            location=row["location"],
            roof_incl=row["roof_incl"],
            roof_azimuth=row["roof_azimuth"],
            electr_cons=row["electr_cons"],
            peak_power=row["peak_power"],
            battery_cap=row["battery_cap"],
            coordinates=coordinates,
            time_created=(
                row["time_created"].isoformat() if row["time_created"] else None
            ),
            model_id=str(row["id"]),
            sim_id=str(row["sim_id"]) if row["sim_id"] is not None else None,
        )

    async def fetch_models(self, user_id: int) -> list[ModelDataOut]:
        """Fetch all models belonging to a user.

        Args:
            user_id (int): The user id that owns the models.

        Returns:
            list[ModelDataOut]: The user's models.

        """
        rows = await self._fetch_all(
            """
            SELECT m.* FROM models m
            WHERE m.user_id = %s ORDER BY m.id
            """,
            (user_id,),
        )
        return [self._model_from_row(row) for row in rows]

    async def fetch_model_by_id(self, model_id: str, user_id: int) -> ModelDataOut:
        """Fetch one user-owned model by its string ID.

        Args:
            model_id (str): The string ID of the model.
            user_id (int): The user id that owns the model.

        Returns:
            ModelDataOut: The requested model.

        """
        internal_id = self._int_id(model_id)
        if internal_id is None:
            raise RuntimeError(f"Failed to fetch model with ID {model_id}")
        row = await self._fetch_one(
            """
            SELECT m.* FROM models m
            WHERE m.id = %s AND m.user_id = %s
            """,
            (internal_id, user_id),
        )
        if row is None:
            raise RuntimeError(f"Failed to fetch model with ID {model_id}")
        return self._model_from_row(row)

    async def update_sim_id_of_model(
        self, model_id: str, sim_id: str, user_id: int
    ) -> bool:
        """Associate a simulation with a user-owned model.

        Args:
            model_id (str): The string ID of the model.
            sim_id (str): The string ID of the simulation.
            user_id (int): The user id that owns the model.

        Returns:
            bool: Whether the model was updated.

        """
        model_pk, sim_pk = self._int_id(model_id), self._int_id(sim_id)
        if model_pk is None or sim_pk is None:
            return False
        return (
            await self._execute(
                """UPDATE models SET sim_id = %s
                WHERE id = %s AND user_id = %s""",
                (sim_pk, model_pk, user_id),
            )
            > 0
        )

    async def delete_model(self, model_id: str, user_id: int) -> bool:
        """Delete a user-owned model and its dependent records.

        Args:
            model_id (str): The string ID of the model.
            user_id (int): The user id that owns the model.

        Returns:
            bool: Whether the model was deleted.

        """
        internal_id = self._int_id(model_id)
        if internal_id is None:
            return False
        return (
            await self._execute(
                """DELETE FROM models WHERE id = %s AND user_id = %s""",
                (internal_id, user_id),
            )
            > 0
        )
