import logging

from components.host import sim_host
from components.database.mongodb import pyMongoClient
from components.dev import (
    sf_house,
    smart_meter,
    baseload,
    pv_sys,
    battery_dev,
)
from components.ctrl import battery_ctrl

logger = logging.getLogger("ferntree")


class SimBuilder:
    def __init__(self, sim_id: str):
        # Connect to database
        self.db_client = pyMongoClient(sim_id)

        # Load simulation config from database
        sim_config = self.db_client.load_config()
        self.system_settings = sim_config["system_settings"]

        # Load simulation input data from database
        # sim_input = self.db_client.load_simulation_input()

        # Set up simulation host
        self.sim = sim_host.SimHost(sim_config, self.db_client)
        self.sim.T_amb = sim_config["T_amb"]
        self.sim.P_solar = sim_config["G_i"]

    def build_simulation(self):
        logger.info("Building simulation...")

        # Create model of single-family house
        if self.system_settings:
            house = sf_house.SfHouse(self.sim)
            sm = smart_meter.SmartMeter(self.sim, house)
            house.add_component(sm, "smart_meter")

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

            # Create baseload
            if self.system_settings["baseload"]:
                # Get load profile for baseload from database
                load_profile = self.db_client.get_load_profile(
                    int(self.system_settings["baseload"]["profile_id"])
                )
                # Create baseload device
                bl = baseload.BaseLoad(
                    self.sim, self.system_settings["baseload"], load_profile
                )
                house.add_component(bl, "baseload")
                logger.info("Baseload added to the house.")
            else:
                logger.error(
                    "No baseload specifications found. Required for simulation!"
                )
                return

            # Create PV system
            if self.system_settings["pv"]:
                pv = pv_sys.PVSys(self.sim, self.system_settings["pv"])
                house.add_component(pv, "pv")
                logger.info("PV system added to the house.")
            else:
                logger.warning("No PV system specifications found.")

            # Create battery
            if self.system_settings["battery"]:
                battery = battery_dev.BatteryDev(
                    self.sim, self.system_settings["battery"]
                )
                battery.battery_ctrl = battery_ctrl.BatteryCtrl(
                    self.sim, self.system_settings["battery"]["battery_ctrl"], sm
                )
                house.add_component(battery, "battery")
                logger.info("Battery added to the house.")
            else:
                logger.warning("No battery specifications found.")

        else:
            logger.error("No model specifications found.")
            return

        logger.info("Simulation built successfully.")
        logger.info("")

        return self.sim
