import logging
from typing import Any

from components.ctrl.battery_ctrl import BatteryCtrl
from components.database.mongodb import pyMongoClient
from components.dev.baseload import BaseLoad
from components.dev.battery_dev import BatteryDev
from components.dev.pv_sys import PVSys
from components.dev.sf_house import SfHouse
from components.dev.smart_meter import SmartMeter
from components.host.sim_host import SimHost

logger = logging.getLogger("ferntree")


class SimBuilder:
    """Class to build the simulation based on the model specifications. It gets the
    simulation and model specs from the database and creates the system model with
    baseload, PV system, and battery.
    """

    def __init__(self, sim_id: str, model_id: str) -> None:
        """Initialize the simulation builder.

        Args:
            sim_id (str): id of simulation doc in db
            model_id (str): id of model doc in db

        """
        # Connect to database
        self.db_client: pyMongoClient = pyMongoClient(sim_id, model_id)

        # Load simulation config from database
        sim_config: dict[str, Any] = self.db_client.load_config()
        self.system_settings: dict[str, Any] = sim_config["system_settings"]

        # Set up simulation host
        self.sim: SimHost = SimHost(sim_config, self.db_client)
        self.sim.T_amb = sim_config["T_amb"]
        self.sim.P_solar = sim_config["G_i"]

    def build_simulation(self) -> SimHost:
        """Build the simulation based on the model specifications.

        Returns:
            sim_host.SimHost: the simulation host

        """
        logger.info("Building simulation...")

        # Create model of single-family house
        if self.system_settings:
            house: SfHouse = SfHouse(self.sim)
            sm: SmartMeter = SmartMeter(self.sim, house)
            house.add_component(sm, "smart_meter")

            # Create baseload
            if self.system_settings["baseload"]:
                # Get load profile for baseload from database
                load_profile: list[float] = self.db_client.get_load_profile(
                    int(self.system_settings["baseload"]["profile_id"])
                )
                # Create baseload device
                bl: BaseLoad = BaseLoad(
                    self.sim, self.system_settings["baseload"], load_profile
                )
                house.add_component(bl, "baseload")
                logger.info("Baseload added to the house.")
            else:
                logger.error(
                    "No baseload specifications found. Required for simulation!"
                )
                raise ValueError("No baseload specifications found.")

            # Create PV system
            if self.system_settings["pv"]:
                pv: PVSys = PVSys(self.sim, self.system_settings["pv"])
                house.add_component(pv, "pv")
                logger.info("PV system added to the house.")
            else:
                logger.warning("No PV system specifications found.")

            # Create battery
            if self.system_settings["battery"]:
                battery: BatteryDev = BatteryDev(
                    self.sim, self.system_settings["battery"]
                )
                battery.battery_ctrl = BatteryCtrl(
                    self.sim, self.system_settings["battery"]["battery_ctrl"], sm
                )
                house.add_component(battery, "battery")
                logger.info("Battery added to the house.")
            else:
                logger.warning("No battery specifications found.")

            # # Create heating system
            # if self.system_settings["heating_sys"]:
            #     heating = heating_sys.HeatingSys(self.sim)
            #     heating.thermal_model = thermal_model.ThermalModel(
            #         self.sim, self.system_settings["heating_sys"]["thermal_model"]
            #     )
            #     heating.heating_ctrl = heating_ctrl.HeatingCtrl(
            #         self.sim, self.system_settings["heating_sys"]["thermostat"]
            #     )
            #     heating.heating_dev = heating_dev.HeatingDev(
            #         self.sim, self.system_settings["heating_sys"]["heating_dev"]
            #     )

            #     house.add_component(heating, "heating")
            #     logger.info("Heating system added to the house.")
            # else:
            #     logger.error(
            #         "No heating system specifications found. Required for simulation!"
            #     )
            #     return

        else:
            logger.error("No model specifications found.")
            raise ValueError("No model specifications found.")

        logger.info("Simulation built successfully.")
        logger.info("")

        return self.sim
