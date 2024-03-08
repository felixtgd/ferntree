import numpy as np
from dev import device

class ThermalModel(device.Device):
    """Class for a thermal building model.
    This model represents the 3R2C thermal model based on a lumped RC-network with three resistances and two capacitances.
    It uses the parameters of the SFH F Var3 model presented in the paper 'Reduced-order models for assessing demand 
    response with heat pumps - Insights from the German energy system' by E. Sperber, U. Frey, V. Bertsch (2020)
    """

    def __init__(self, host):
        """Initializes a new instance of the ThermalModel class.
        """

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

        # Initialize thermal state
        self.T_in = 20 + 273.15 # indoor temperature [K]
        self.T_en = 20 + 273.15 # building envelope temperature [K]

        # Pre-calculate time constants
        self.dt = self.host.timebase / 3600
        self.timebase_sqrt = np.sqrt(self.host.timebase)


    def compute_thermal_response(self, T_amb, P_solar, P_hgain, P_heat_th):
        """
        Compute the thermal response of the building.

        Args:
            T_amb (float): Ambient temperature [K]
            P_solar (float): Solar irradiance [kW/m2]
            P_hgain (float): Internal heat gain [kW]
            P_heat_th (float): Thermal heating power [kW]

        Returns:
            Tuple[float, float]: The updated indoor and envelope temperatures.

        """
        # Thermal RC-model of building
        dTi = (
            1.0 / (self.Ci * self.Rie) * (self.T_en - self.T_in)
            + 1.0 / (self.Ci * self.Ria) * (T_amb - self.T_in)
            + self.Ai / self.Ci * P_solar
            + 1.0 / self.Ci * (P_heat_th + P_hgain)
        ) * self.dt  + np.random.normal()/self.timebase_sqrt
        dTe = (
            1.0 / (self.Ce * self.Rie) * (self.T_in - self.T_en)
            + 1.0 / (self.Ce * self.Rea) * (T_amb - self.T_en)
        ) * self.dt  + np.random.normal()/self.timebase_sqrt

        # Update temperatures
        self.T_in += dTi
        self.T_en += dTe

        return self.T_in, self.T_en
