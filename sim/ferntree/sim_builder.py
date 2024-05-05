import logging

from host import sim_host
from database.mongodb import pyMongoClient
from dev import (
    sf_house,
    smart_meter,
    baseload,
    pv_sys,
    battery_dev,
)
from ctrl import battery_ctrl

logger = logging.getLogger("ferntree")


class SimBuilder:
    def __init__(self, sim_id: str, model_id: str):
        # Connect to database
        self.db_client = pyMongoClient(model_id, sim_id)

        # Load model specifications from database
        config = self.db_client.load_config()
        sim_params = config["sim_model_specs"]["sim_params"]
        self.model_specs = config["sim_model_specs"]["house"]

        # Load simulation input data from database
        sim_input = self.db_client.load_simulation_input()

        # Set up simulation host
        self.sim = sim_host.SimHost(sim_params, self.db_client)
        self.sim.T_amb = sim_input["T_amb"]
        self.sim.P_solar = sim_input["G_i"]

    def build_simulation(self):
        logger.info("Building simulation...")

        # Create model of single-family house
        if self.model_specs:
            house = sf_house.SfHouse(self.sim)
            sm = smart_meter.SmartMeter(self.sim, house)
            house.add_component(sm, "smart_meter")

            # # Create heating system
            # if self.model_specs["heating_sys"]:
            #     heating = heating_sys.HeatingSys(self.sim)
            #     heating.thermal_model = thermal_model.ThermalModel(
            #         self.sim, self.model_specs["heating_sys"]["thermal_model"]
            #     )
            #     heating.heating_ctrl = heating_ctrl.HeatingCtrl(
            #         self.sim, self.model_specs["heating_sys"]["thermostat"]
            #     )
            #     heating.heating_dev = heating_dev.HeatingDev(
            #         self.sim, self.model_specs["heating_sys"]["heating_dev"]
            #     )

            #     house.add_component(heating, "heating")
            #     logger.info("Heating system added to the house.")
            # else:
            #     logger.error(
            #         "No heating system specifications found. Required for simulation!"
            #     )
            #     return

            # Create baseload
            if self.model_specs["baseload"]:
                # Get load profile for baseload from database
                load_profile = self.db_client.get_load_profile(
                    int(self.model_specs["baseload"]["profile_id"])
                )
                # Create baseload device
                bl = baseload.BaseLoad(
                    self.sim, self.model_specs["baseload"], load_profile
                )
                house.add_component(bl, "baseload")
                logger.info("Baseload added to the house.")
            else:
                logger.error(
                    "No baseload specifications found. Required for simulation!"
                )
                return

            # Create PV system
            if self.model_specs["pv"]:
                pv = pv_sys.PVSys(self.sim, self.model_specs["pv"])
                house.add_component(pv, "pv")
                logger.info("PV system added to the house.")
            else:
                logger.warning("No PV system specifications found.")

            # Create battery
            if self.model_specs["battery"]:
                battery = battery_dev.BatteryDev(self.sim, self.model_specs["battery"])
                battery.battery_ctrl = battery_ctrl.BatteryCtrl(
                    self.sim, self.model_specs["battery"]["battery_ctrl"], sm
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
