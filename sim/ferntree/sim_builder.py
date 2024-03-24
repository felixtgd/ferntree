import json
import os
import logging

from host import sim_host
from dev import sf_house, heating_sys, heating_dev
from ctrl import heating_ctrl
from models import thermal_model

logger = logging.getLogger("ferntree")

class SimBuilder():
    def __init__(self, model_path):
       # Load simulation settings and model specifications
        with open(os.path.join(model_path, "model_config.json")) as f:
            config = json.load(f)
            self.model_specs = config["house"]
            self.sim_settings = config["sim"]
        
        # Set up simulation host
        self.sim = sim_host.SimHost(self.sim_settings)
        self.sim.weather_data_path = os.path.join(model_path, "env_data.json")


    def build_simulation(self):
        logger.info("Building simulation...")

        # Create model of single-family house
        if self.model_specs:
            house = sf_house.SfHouse(self.sim)

            # Create heating system
            if self.model_specs["heating_sys"]:
                heating = heating_sys.HeatingSys(self.sim)
                heating.thermal_model = thermal_model.ThermalModel(self.sim, self.model_specs["heating_sys"]["thermal_model"])
                heating.heating_ctrl = heating_ctrl.HeatingCtrl(self.sim, self.model_specs["heating_sys"]["thermostat"])
                heating.heating_dev = heating_dev.HeatingDev(self.sim, self.model_specs["heating_sys"]["heating_dev"])

                house.add_component(heating, "heating")
                logger.info("Heating system added to the house.")
            else:
                logger.error("No heating system specifications found. Required for simulation!")
                return
            
            # Create baseload
            if self.model_specs["baseload"]:
                # baseload = Baseload(self.sim, self.model_specs["baseload"])
                # house.add_component(baseload)
                logger.info("Baseload added to the house.")
            else:
                logger.error("No baseload specifications found. Required for simulation!")
                # return
            
            # Create PV system
            if self.model_specs["pv"]:
                # pv = PV(self.sim, self.model_specs["pv"])
                # house.add_component(pv)
                logger.info("PV system added to the house.")
            else:
                logger.warning("No PV system specifications found.")
                
            # Create battery
            if self.model_specs["battery"]:
                # battery = Battery(self.sim, self.model_specs["battery"])
                # house.add_component(battery)
                logger.info("Battery added to the house.")
            else:
                logger.warning("No battery specifications found.")

        else:
            logger.error("No model specifications found.")
            return
        
        logger.info("Simulation built successfully.")
        logger.info("")
        
        return self.sim



       
        