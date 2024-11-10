import logging
from datetime import datetime
from typing import Any, Optional, Union

from pytz import timezone

from components.database.mongodb import pyMongoClient
from components.dev.sf_house import SfHouse

logger = logging.getLogger("ferntree")


class SimHost:
    """Main component of the simulation. Responsible for:
    - Setting up the simulation environment
    - Handling weather data
    - Running the simulation
    - Saving the results to the database.
    """

    def __init__(self, sim_settings: dict[str, Any], db_client: pyMongoClient) -> None:
        """Initializes a new instance of the SimHost class.

        Args:
            sim_settings (dict): Simulation settings
            db_client (pyMongoClient): MongoDB database client

        """
        self.db_client: pyMongoClient = db_client  # MongoDB database client

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

        self.house: SfHouse  # House object being simulated

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
        """Startup of the host:
        - Initializes the current time.
        - Starts up the house.
        """
        self.current_time = self.start_time
        self.house.startup()

    def shutdown(self) -> None:
        """Shutdown of the host:
        - Shuts down the database.
        - Shuts down the house.
        """
        self.db_client.shutdown()
        self.house.shutdown()

    def add_house(self, house: SfHouse) -> None:
        """Adds a house to the simulation host."""
        if isinstance(house, SfHouse):
            self.house = house
        else:
            raise TypeError("Can only add objects of class 'House' to simHost.")

    def run_simulation(self) -> None:
        """Runs the simulation.
        - Starts up the host.
        - Perfroms timetick for each timestep in the simulation.
        - Shuts down the host.
        """
        self.startup()
        logger.info(f"Running simulation with {self.timesteps} timesteps.\n")
        for t in range(self.timesteps):
            self.current_timestep = t
            self.timetick(t)

        logger.info("Simulation finished successfully.")
        self.shutdown()

    def timetick(self, t: int) -> None:
        """Performs a timetick for the current timestep.
        - Updates the state of the simulation environment, i.e. time, ambient
        temperature and solar irradiance
        - Triggers the house to perform a timetick
        - Saves the results of the house to the database
        - Updates the current time.
        """
        self.updateState(t)
        results: dict[str, Any] = self.house.timetick()
        self.save_results(results)
        self.current_time += self.timebase

    def updateState(self, t: int) -> None:
        """Updates the state of the simulation environment."""
        self.env_state = {
            "time": self.current_time,
            "T_amb": self.T_amb[t],
            "P_solar": self.P_solar[t],
        }

    def save_results(self, results: dict[str, Any]) -> None:
        """Saves the results of the house to the database."""
        self.db_client.write_timeseries_data_to_db(results)
