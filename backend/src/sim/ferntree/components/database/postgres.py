import os
from typing import Any

import psycopg
from components.database.models import TimestepData
from dotenv import load_dotenv
from psycopg.rows import dict_row

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "../../../../../.env"))
DATABASE_URL = os.environ["DATABASE_URL"]


class PostgresClient:
    """Synchronous PostgreSQL client used by the simulation subprocess."""

    def __init__(self, sim_id: str, model_id: str) -> None:
        """Open the database connection and replace prior simulation results."""
        try:
            self.sim_id = int(sim_id)
            self.model_id = int(model_id)
        except (TypeError, ValueError) as error:
            raise ValueError("Simulation and model IDs must be integers") from error

        self.client: psycopg.Connection[Any] = psycopg.connect(DATABASE_URL)
        self.batch_size = 1000
        self.data_buffer: list[TimestepData] = []

        with self.client.cursor() as cur:
            cur.execute("DELETE FROM sim_timesteps WHERE sim_id = %s", (self.sim_id,))
        self.client.commit()

    def load_config(self) -> dict[str, Any]:
        """Load the flat simulation configuration from PostgreSQL."""
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
            "baseload_profile_id": result["baseload_profile_id"],
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
        """Get a complete load profile array from PostgreSQL."""
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

    def write_timeseries_data_to_db(self, results: dict[str, Any]) -> None:
        """Validate and buffer one timestep, flushing full batches."""
        parsed_results = TimestepData(**results)
        self.data_buffer.append(parsed_results)

        if len(self.data_buffer) == self.batch_size:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

    def write_batch(self, batch: list[TimestepData]) -> None:
        """Bulk insert a batch of timestep results."""
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
        """Flush buffered results and close the database connection."""
        if self.data_buffer:
            self.write_batch(self.data_buffer)
            self.data_buffer = []
        self.client.close()
