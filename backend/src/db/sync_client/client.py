"""Provide synchronous PostgreSQL access for the simulation engine."""

from typing import Any

import psycopg
from psycopg.rows import dict_row

from src.db.config import DATABASE_URL
from src.db.schemas import SimTimestep


class PostgresClient:
    """Manage synchronous PostgreSQL access for one simulation run.

    The client owns one database connection for the lifetime of the simulation
    and buffers timestep writes before committing them in batches.
    """

    def __init__(self, sim_id: str, model_id: str) -> None:
        """Open the connection and remove prior results for the simulation.

        Args:
            sim_id: The string identifier of the simulation to run.
            model_id: The string identifier of the model being simulated.

        Raises:
            ValueError: If either identifier cannot be converted to an integer.
            psycopg.Error: If the database connection or cleanup query fails.

        """
        try:
            self.sim_id = int(sim_id)
            self.model_id = int(model_id)
        except (TypeError, ValueError) as error:
            raise ValueError("Simulation and model IDs must be integers") from error

        self.client: psycopg.Connection[Any] = psycopg.connect(DATABASE_URL)
        self.batch_size = 1000
        self.data_buffer: list[SimTimestep] = []

        with self.client.cursor() as cur:
            cur.execute("DELETE FROM sim_timesteps WHERE sim_id = %s", (self.sim_id,))
        self.client.commit()

    def load_config(self) -> dict[str, Any]:
        """Load the flat simulation configuration from PostgreSQL.

        Returns:
            A dictionary containing the persisted simulation settings used by
            the simulation builder.

        Raises:
            ValueError: If the simulation does not exist.
            psycopg.Error: If the database query fails.

        """
        with self.client.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM simulations WHERE id = %s", (self.sim_id,))
            result = cur.fetchone()

        if result is None:
            raise ValueError(f"Simulation with id {self.sim_id} not found in database.")

        return {
            "timebase": result["timebase"],
            "timezone": result["timezone"],
            "T_amb": result["t_amb"],
            "G_i": result["g_i"],
            "baseload_annual_consumption": result["baseload_annual_consumption"],
            "pv_roof_tilt": result["pv_roof_tilt"],
            "pv_roof_azimuth": result["pv_roof_azimuth"],
            "pv_peak_power": result["pv_peak_power"],
            "battery_capacity": result["battery_capacity"],
            "battery_max_power": result["battery_max_power"],
            "battery_soc_init": result["battery_soc_init"],
            "batctrl_planning_horizon": result["batctrl_planning_horizon"],
            "batctrl_useable_capacity": result["batctrl_useable_capacity"],
            "batctrl_greedy": result["batctrl_greedy"],
            "batctrl_opt_fill": result["batctrl_opt_fill"],
        }

    def get_load_profile(self, profile_id: int) -> list[float]:
        """Get a complete load profile array from PostgreSQL.

        Args:
            profile_id: The database identifier of the load profile.

        Returns:
            The load profile values in database order.

        Raises:
            ValueError: If the load profile does not exist.
            psycopg.Error: If the database query fails.

        """
        with self.client.cursor() as cur:
            cur.execute(
                "SELECT load_profile FROM loadprofiles WHERE profile_id = %s",
                (profile_id,),
            )
            row = cur.fetchone()

        if row is None:
            raise ValueError(
                f"Load profile with id {profile_id} not found in database."
            )
        return list(row[0])

    def ensure_load_profile(
        self, profile_id: int, profile_type: str, load_profile: list[float]
    ) -> None:
        """Insert or refresh a load profile, overwriting any existing row.

        Args:
            profile_id: The database identifier of the load profile.
            profile_type: A human-readable label describing the profile.
            load_profile: The normalized load profile values to persist.

        Raises:
            psycopg.Error: If the upsert or commit fails.

        """
        with self.client.cursor() as cur:
            cur.execute(
                """
                INSERT INTO loadprofiles (profile_id, type, load_profile)
                VALUES (%s, %s, %s)
                ON CONFLICT (profile_id) DO UPDATE SET
                    type = EXCLUDED.type,
                    load_profile = EXCLUDED.load_profile
                """,
                (profile_id, profile_type, load_profile),
            )
        self.client.commit()

    def write_timeseries_data_to_db(self, results: dict[str, Any]) -> None:
        """Validate and buffer one timestep, flushing full batches.

        Args:
            results: The raw timestep values produced by the simulation engine.

        Raises:
            pydantic.ValidationError: If the timestep values are invalid.
            psycopg.Error: If a full batch cannot be written.

        """
        parsed_results = SimTimestep(**results)
        self.data_buffer.append(parsed_results)

        if len(self.data_buffer) == self.batch_size:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

    def write_batch(self, batch: list[SimTimestep]) -> None:
        """Bulk insert a batch of timestep results.

        Args:
            batch: The validated timestep models to insert.

        Raises:
            psycopg.Error: If the bulk insert or commit fails.

        """
        columns = (
            "sim_id",
            "time",
            "t_amb",
            "p_solar",
            "p_base",
            "p_pv",
            "p_bat",
            "soc_bat",
            "fill_level",
            "p_load_pred",
        )
        with self.client.cursor() as cur:
            with cur.copy(
                f"COPY sim_timesteps ({','.join(columns)}) FROM STDIN"
            ) as copy:
                for result in batch:
                    copy.write_row(
                        (
                            self.sim_id,
                            result.time,
                            result.T_amb,
                            result.P_solar,
                            result.P_base,
                            result.P_pv,
                            result.P_bat,
                            result.Soc_bat,
                            result.fill_level,
                            result.P_load_pred,
                        )
                    )
        self.client.commit()

    def shutdown(self) -> None:
        """Flush buffered results and close the database connection.

        Raises:
            psycopg.Error: If flushing the remaining results or closing the
                connection fails.

        """
        if self.data_buffer:
            self.write_batch(self.data_buffer)
            self.data_buffer = []
        self.client.close()
