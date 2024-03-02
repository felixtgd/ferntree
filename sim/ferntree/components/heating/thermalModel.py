import numpy as np 
from component import Component

class ThermalModel(Component):

    def __init__(self) -> None:

        super().__init__()

        # SFH F Var3 Model parameters
        self.Ai = 1.72
        self.Ce = 16.39
        self.Ci = 2.02
        self.Rea = 13.26
        self.Ria = 24.38
        self.Rie = 0.53

        # Thermal state
        self.T_amb = None # ambient temperature [K]
        self.T_in = 20 + 273.15 # indoor temperature [K]
        self.T_en = 20 + 273.15 # building envelope temperature [K]
        self.P_solar = None # solar irradiance [kw/m2]
        self.P_hgain = None # internal heat gains [kW]
        self.P_heat = None # heating power [kW]

    def compute_thermal_response(self, T_amb, P_solar, P_hgain, P_heat):
        # Thermal RC-model of building 
        dTi = (1.0/(self.Ci * self.Rie) * (self.T_en - self.T_in) + 1.0/(self.Ci * self.Ria) * (T_amb - self.T_in) + self.Ai / self.Ci * P_solar + 1.0/self.Ci * (P_heat + P_hgain)) # + si * dwi
        dTe = (1.0/(self.Ce * self.Rie) * (self.T_in - self.T_en) + 1.0/(self.Ce * self.Rea) * (T_amb - self.T_en)) # + si * dwi
        
        # Update temperatures
        self.T_in += dTi
        self.T_en += dTe

        return self.T_in, self.T_en