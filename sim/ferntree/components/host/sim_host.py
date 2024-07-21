import json
import logging
import os
from pytz import timezone
from datetime import datetime

from sim.ferntree.components.dev import sf_house

# from database import database
from sim.ferntree.components.database.mongodb import pyMongoClient

logger = logging.getLogger("ferntree")


class SimHost:
    """Main component of the simulation. Responsible for:
    - Setting up the simulation environment
    - Handling weather data
    - Running the simulation
    - Saving the results to the database
    """

    def __init__(self, sim_settings: dict, db_client: pyMongoClient):
        """
        Initializes a new instance of the SimHost class.
        """

        self.db_client = db_client  # MongoDB database client

        # self.model_name = sim_settings["model_name"]
        self.timebase = int(sim_settings["timebase"])  # Timebase in seconds
        self.timesteps = int(365 * 24 * 3600 / self.timebase)  # Number of timesteps
        self.timezone = timezone(sim_settings["timezone"])
        # self.start_time = int(datetime(2023, 1, 1).timestamp())  # Start time in seconds since epoch
        self.start_time = int(
            self.timezone.localize(datetime(2023, 1, 1)).timestamp()
        )  # Start time in seconds since epoch
        self.current_time = None  # Current time in seconds since epoch
        self.current_timestep = None  # Current timestep

        self.house = None  # House object being simulated

        self.env_state = {  # Current state of simulation environment
            "time": None,  # Time of the simulation
            "T_amb": None,  # Ambient temperature [K]
            "P_solar": None,  # Solar irradiance [kW/m2]
        }

        # self.weather_data_path = None  # Path to the weather data file
        self.T_amb = None
        self.P_solar = None

    def startup(self):
        """
        Startup of the host:
        - Initializes the current time
        - Starts up the house
        """
        self.current_time = self.start_time
        # self.db = database.PostgresDatabase()
        # self.db.startup()
        # self.load_weather_data()
        self.house.startup()

    def shutdown(self):
        """
        Shutdown of the host:
        - Shuts down the database
        - Shuts down the house
        """
        self.db_client.shutdown()
        self.house.shutdown()

        # Prototype of results export
        # self.export_results()

    def add_house(self, house: sf_house.SfHouse):
        """Adds a house to the simulation host."""
        if isinstance(house, sf_house.SfHouse):
            self.house = house
        else:
            raise TypeError("Can only add objects of class 'House' to simHost.")

    def run_simulation(self):
        """Runs the simulation.
        - Starts up the host
        - Perfroms timetick for each timestep in the simulation
        - Shuts down the host
        """
        self.startup()
        logger.info(f"Running simulation with {self.timesteps} timesteps.\n")
        for t in range(self.timesteps):
            self.current_timestep = t
            self.timetick(t)

        logger.info("Simulation finished successfully.")
        self.shutdown()

    def timetick(self, t):
        """Performs a timetick for the current timestep.
        - Updates the state of the simulation environment, i.e. time, ambient temperature and solar irradiance
        - Triggers the house to perform a timetick
        - Saves the results of the house to the database
        - Updates the current time
        """
        self.updateState(t)
        results = self.house.timetick()
        self.save_results(results)
        self.current_time += self.timebase

    def updateState(self, t):
        """Updates the state of the simulation environment."""
        self.env_state = {
            "time": self.current_time,
            "T_amb": self.T_amb[t],
            "P_solar": self.P_solar[t],
        }

    def save_results(self, results):
        """Saves the results of the house to the database."""
        self.db_client.write_timeseries_data_to_db(results)

    # def get_load_profile(self, profile_id):
    #     """Gets a load profile for the baseload from the database."""
    #     load_profile = self.db.get_load_profile(profile_id)

    #     if len(load_profile) != self.timesteps:
    #         raise ValueError("Load profile length does not match number of timesteps.")
    #     else:
    #         return load_profile

    # # NOTE: Only for prototyping, will be replaced by database access
    # # TODO: Need two solar irradiances: global horizontal for house and beam on tilted plane for PV
    # def load_weather_data(self):
    #     """Loads the weather data from the weather data file."""
    #     with open(self.weather_data_path) as json_file:
    #         input_data = json.load(json_file)
    #         hourly_data = input_data["outputs"]["hourly"]
    #         self.T_amb = [hd["T2m"] + 273.15 for hd in hourly_data]  # [K]
    #         # self.P_solar = [hd["Gb(i)"] / 1e3 for hd in hourly_data]  # [kW/m2]
    #         self.P_solar = [hd["G(i)"] / 1e3 for hd in hourly_data]  # [kW/m2]

    # PROTOTYPE: Export results to json file, later to database
    def export_results(self):
        """Exports the results of the simulation to a json file."""
        results_df = self.db.get_sim_results()

        annual_baseload_demand = results_df["P_base"].sum()
        annual_pv_generation = (
            abs(results_df["P_pv"].sum()) + results_df["Soc_bat"].iloc[-1]
        )
        annual_grid_consumption = results_df["P_total"][
            results_df["P_total"] > 0.0
        ].sum()
        annual_grid_feed_in = abs(
            results_df["P_total"][results_df["P_total"] < 0.0].sum()
        )
        annual_self_consumption = annual_baseload_demand - annual_grid_consumption

        # Create results dictionary with model specifications and simulation results
        results = {
            "model": {
                "pv_size": self.house.components["pv"].peak_power,
                "bat_cap": self.house.components["battery"].capacity,
                "bat_pwr": self.house.components["battery"].max_power,
            },
            "results": {
                "annual_baseload_demand": annual_baseload_demand,
                "annual_pv_generation": annual_pv_generation,
                "annual_grid_consumption": annual_grid_consumption,
                "annual_grid_feed_in": annual_grid_feed_in,
                "annual_self_consumption": annual_self_consumption,
            },
        }

        file_path = os.path.join(
            os.getcwd(), f"sim/workspace/{self.model_name}/results.json"
        )
        with open(file_path, "w") as json_file:
            json.dump(results, json_file, indent=4)

        logger.info("Results exported to results.json.\n")

        logger.info(f"PV size: {results['model']['pv_size']} kWp")
        logger.info(f"Battery capacity: {results['model']['bat_cap']} kWh")
        logger.info(f"Battery power: {results['model']['bat_pwr']} kW\n")

        logger.info(f"Annual baseload demand: {annual_baseload_demand:.2f} kWh")
        logger.info(f"Annual PV generation: {annual_pv_generation:.2f} kWh")
        logger.info(f"Annual grid consumption: {annual_grid_consumption:.2f} kWh")
        logger.info(f"Annual grid feed-in: {annual_grid_feed_in:.2f} kWh")
        logger.info(
            f"Annual self-consumption: {annual_self_consumption:.2f} kWh ({(annual_self_consumption/annual_baseload_demand * 100):.2f}%)"
        )
