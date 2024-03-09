import numpy as np

from dev import device

class ThermalModel(device.Device):
    """Class for a thermal building model.
    This model represents the 3R2C thermal model based on a lumped RC-network with three resistances and two capacitances.
    It uses the parameters of the SFH F Var3 model presented in the paper 'Reduced-order models for assessing demand 
    response with heat pumps - Insights from the German energy system' by E. Sperber, U. Frey, V. Bertsch (2020)
    """

    def __init__(self, host, model_specs):
        """Initializes a new instance of the ThermalModel class.
        """

        super().__init__(host)

        self.model_order = "2R3C"  # 2 resistances and 3 capacitances in lumped RC-network
        self.yoc = model_specs["yoc"]  # year of construction
        self.heated_area = model_specs["heated_area"]  # heated living area [m2]
        self.heat_gain = 3.0 / 1e3  # internal heat gain, constant at 3 W/m2
        self.P_hgain = self.heated_area * self.heat_gain  # internal heat gain [kW]

        # Renovations:
        # Var1: original condition at construction of the building
        # Var2: conventional renovation with moderate insulation of the building shell and window replacement with two-panes glazing
        # Var3: deep renovation with high insulation and three-panes glazing
        self.renovation = model_specs["renovation"]  # state of renovation 
        
        # Set the model parameters 
        self.set_model_params()

        # Pre-calculate time constants
        self.dt = self.host.timebase / 3600
        self.timebase_sqrt = np.sqrt(self.host.timebase)


    def set_model_params(self):
        #TODO: Change this later to dynamically set parameters based on yoc, heated_area, and renovation
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


    def compute_thermal_response(self, T_in, T_en, T_amb, P_solar, P_heat_th):
        """
        Compute the thermal response of the building.

        Args:
            T_in (float): Indoor temperature [K]
            T_en (float): Building envelope temperature [K]
            T_amb (float): Ambient temperature [K]
            P_solar (float): Solar irradiance [kW/m2]
            P_heat_th (float): Thermal heating power [kW]

        Returns:
            Tuple[float, float]: The updated indoor and envelope temperatures.

        """
        # Thermal RC-model of building
        dTi = (
            1.0 / (self.Ci * self.Rie) * (T_en - T_in)
            + 1.0 / (self.Ci * self.Ria) * (T_amb - T_in)
            + self.Ai / self.Ci * P_solar
            + 1.0 / self.Ci * (P_heat_th + self.P_hgain)
        ) * self.dt  + np.random.normal()/self.timebase_sqrt
        dTe = (
            1.0 / (self.Ce * self.Rie) * (T_in - T_en)
            + 1.0 / (self.Ce * self.Rea) * (T_amb - T_en)
        ) * self.dt  + np.random.normal()/self.timebase_sqrt

        # Update temperatures
        T_in += dTi
        T_en += dTe

        return T_in, T_en
