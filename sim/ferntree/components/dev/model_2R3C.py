import numpy as np
from dev import device

class ThermalModel(device.Device):

    def __init__(self, host) -> None:

        super().__init__(host)

        # SFH F Var3 Model parameters
        # Effective window area for absorption of solar gains on internal air [m2]
        self.Ai = 1.72 
        # Capacitance of building envelope [kWh/K]
        self.Ce = 16.39
        # Capacitance of interior [kWh/K]
        self.Ci = 2.02
        # Thermal resistance between building envelope and the ambient [K/kW]
        self.Rea = 13.26
        # Thermal resistance between interior and the ambient [K/kW]
        self.Ria = 24.38
        # Thermal resistance between interior and building envelope [K/kW]
        self.Rie = 0.53

        # Thermal state
        self.T_in = 20 + 273.15 # indoor temperature [K]
        self.T_en = 20 + 273.15 # building envelope temperature [K]


    def compute_thermal_response(self, T_amb, P_solar, P_hgain, P_heat):
        """
        Compute the thermal response of the building.

        Args:
            T_amb (float): Ambient temperature in Kelvin.
            P_solar (float): Solar power input in Watts.
            P_hgain (float): Heat gain power input in Watts.
            P_heat (float): Heat power input in Watts.

        Returns:
            Tuple[float, float]: The updated indoor and envelope temperatures.

        """
        # Thermal RC-model of building
        dTi = (
            1.0 / (self.Ci * self.Rie) * (self.T_en - self.T_in)
            + 1.0 / (self.Ci * self.Ria) * (T_amb - self.T_in)
            + self.Ai / self.Ci * P_solar
            + 1.0 / self.Ci * (P_heat + P_hgain)
        ) * self.host.timebase / 3600  + np.random.normal()/np.sqrt(self.host.timebase)
        dTe = (
            1.0 / (self.Ce * self.Rie) * (self.T_in - self.T_en)
            + 1.0 / (self.Ce * self.Rea) * (T_amb - self.T_en)
        ) * self.host.timebase / 3600  + np.random.normal()/np.sqrt(self.host.timebase)

        # Update temperatures
        self.T_in += dTi
        self.T_en += dTe

        return self.T_in, self.T_en
