import json
import pandas as pd
import numpy as np

from component import Component
from heatingCtrl import HeatingCtrl
from thermalModel import ThermalModel
from heatingSys import HeatingSys

class Heating(Component):
    
    def __init__(self, 
                 heating_controller:        HeatingCtrl, 
                 thermal_building_model:    ThermalModel, 
                 heating_system:            HeatingSys) -> None:
        
        super().__init__()
        
        self.heatingCtrl = heating_controller
        self.thermalModel = thermal_building_model
        self.heatingSys = heating_system

    # Inputs
    def get_input_data(self):
        with open("example_input_data.json") as json_file:
            input_data = json.load(json_file)
            hourly_data = pd.DataFrame(input_data["outputs"]["hourly"])
            self.Ta = np.array(hourly_data["T2m"]) + 273.15 # [K]
            self.Ps = np.array(hourly_data["Gb(i)"]) /1e3 # [kW/m2]

        # Simulation parameters
        self.timesteps = len(self.Ta)