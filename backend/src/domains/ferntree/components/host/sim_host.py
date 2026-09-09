"""Coordinate simulation timing, components, and persistence."""

import logging
from datetime import datetime
from typing import Any, Optional, Protocol, Union

from pytz import timezone

from src.db.sync_client.client import PostgresClient

logger = logging.getLogger("ferntree")


class House(Protocol):
    """Interface required from the house controlled by a simulation host."""

    def startup(self) -> None:
        """Initialize the house before simulation begins."""

    def shutdown(self) -> None:
        """Release house resources after simulation ends."""

    def timetick(self) -> dict[str, Any]:
        """Advance the house and return its timestep results."""


class SimHost:
    """Coordinate the simulation environment, house, and persistence.

    The host initializes the simulation clock, supplies weather data to the
    simulated house, and persists each timestep's results.
    """

    def __init__(self, sim_settings: dict[str, Any], db_client: PostgresClient) -> None:
        """Initialize a simulation host.

        Args:
            sim_settings: Simulation settings loaded from PostgreSQL.
            db_client: Synchronous PostgreSQL client for the simulation run.

        """
        self.db_client: PostgresClient = db_client

        # self.model_name = sim_settings["model_name"]
        self.timebase: int = int(sim_settings["timebase"])  # Timebase in seconds
        self.timesteps: int = int(
            365 * 24 * 3600 / self.timebase
        )  # Number of timesteps
        self.timezone = timezone(sim_settings["timezone"])
        self.start_time: int = int(
            self.timezone.localize(datetime(2023, 1, 1)).timestamp()
        )  # Start time in seconds since epoch
        self.current_time: int  # Current time in seconds since epoch
        self.current_timestep: int  # Current timestep

        self.house: House  # House object being simulated

        # Current state of simulation environment
        self.env_state: dict[str, Optional[Union[float, int]]] = {
            "time": None,  # Time of the simulation
            "T_amb": None,  # Ambient temperature [K]
            "P_solar": None,  # Solar irradiance [kW/m2]
        }

        # self.weather_data_path = None  # Path to the weather data file
        self.T_amb: list[float]
        self.P_solar: list[float]

    def startup(self) -> None:
        """Initialize the simulation clock and start the house."""
        self.current_time = self.start_time
        self.house.startup()

    def shutdown(self) -> None:
        """Flush database results and shut down the house."""
        self.db_client.shutdown()
        self.house.shutdown()

    def add_house(self, house: House) -> None:
        """Add a house to the simulation host.

        Args:
            house: The house entity to associate with this host.

        Raises:
            TypeError: If ``house`` is not an ``Entity`` instance.

        """
        self.house = house

    def run_simulation(self) -> None:
        """Run the simulation from startup through shutdown.

        The host advances once for each configured timestep and flushes the
        database client when the simulation finishes.
        """
        self.startup()
        logger.info(f"Running simulation with {self.timesteps} timesteps.\n")
        for t in range(self.timesteps):
            self.current_timestep = t
            self.timetick(t)

        logger.info("Simulation finished successfully.")
        self.shutdown()

    def timetick(self, t: int) -> None:
        """Advance the simulation by one timestep.

        Args:
            t: The zero-based index of the current timestep.

        The method updates the environment, advances the house, persists the
        results, and updates the current simulation time.

        """
        self.updateState(t)
        results: dict[str, Any] = self.house.timetick()
        self.save_results(results)
        self.current_time += self.timebase

    def updateState(self, t: int) -> None:
        """Update the state of the simulation environment.

        Args:
            t: The zero-based index used to read weather data.

        """
        self.env_state = {
            "time": self.current_time,
            "T_amb": self.T_amb[t],
            "P_solar": self.P_solar[t],
        }

    def save_results(self, results: dict[str, Any]) -> None:
        """Save the current house results through the database client.

        Args:
            results: The timestep values produced by the simulated house.

        """
        self.db_client.write_timeseries_data_to_db(results)
