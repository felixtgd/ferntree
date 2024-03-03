# import json
# import pandas as pd
# import numpy as np

from components.component import Component
from components.heating.heatingCtrl import HeatingCtrl
from components.heating.thermalModel import ThermalModel
from components.heating.heatingSys import HeatingSys

class Heating(Component):
    
    def __init__(self) -> None:
        
        super().__init__()
        
        # Settings
        self.temp_setpoint = 20 + 273.15 # temperature setpoint in [K]
        self.deadband = 1 # deadband around setpoint
        self.P_heat_max = 3.9 # maximum heating power of system [kW]
        self.heated_area = 158 # heated living area [m2]
        self.P_hgain = 3/1e3 * self.heated_area # internal heat gains constant at 3 W/m2

        # Thermostat controller for heating system
        self.heatingCtrl = HeatingCtrl(self.temp_setpoint, self.deadband, self.P_heat_max)
        
        # Thermal building model
        self.thermalModel = ThermalModel()
        self.thermalModel.T_in = self.temp_setpoint
        self.thermalModel.T_en = self.temp_setpoint

        # Heating system
        self.heatingSys = HeatingSys()
        
        # Current state of the thermal model and heating system
        self.currentState = {"timestep": None,
                             "T_amb": None,
                             "T_in": self.temp_setpoint,
                             "T_en": self.temp_setpoint,
                             "P_solar": None,
                             "P_hgain": self.P_hgain,
                             "P_heat_th": 0.0}

    def updateState(self):
        self.currentState["timestep"] = self.host.env_state["t"]
        self.currentState["T_amb"] = self.host.env_state["T_amb"]
        self.currentState["P_solar"] = self.host.env_state["P_solar"]

    def timetick(self):
        self.updateState()
        # State variables of current timestep (updated by simHost)
        T_amb = self.currentState["T_amb"]
        P_solar = self.currentState["P_solar"]

        P_hgain = self.currentState["P_hgain"]
        P_heat_th = self.currentState["P_heat_th"]
        T_in = self.currentState["T_in"]

        P_heat_th_next = self.heatingCtrl.set_heating_power(T_in, P_heat_th)
        T_in, T_en = self.thermalModel.compute_thermal_response(T_amb, P_solar, P_hgain, P_heat_th_next)
        
        self.currentState["T_in"] = T_in
        self.currentState["T_en"] = T_en
        self.currentState["P_heat_th"] = P_heat_th_next

