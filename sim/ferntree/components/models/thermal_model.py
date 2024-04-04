import numpy as np
import logging
import os

from dev import device
from models import linear_regression

logger = logging.getLogger("ferntree")


class ThermalModel(device.Device):
    """Class for a thermal building model.
    This model represents the 3R2C thermal model based on a lumped RC-network with three resistances and two capacitances.
    It uses a linear regression model to approximate the model parameters presented in the paper
    'Reduced-order models for assessing demand response with heat pumps - Insights from the German energy system'
    by E. Sperber, U. Frey, V. Bertsch (2020)
    """

    def __init__(self, host, model_specs):
        """Initializes a new instance of the ThermalModel class."""

        super().__init__(host)

        self.model_order = (
            "3R2C"  # 2 resistances and 3 capacitances in lumped RC-network
        )
        self.dataset = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/3R2C_model_params_heat_demand.csv",
        )
        self.model = linear_regression.LinearRegressionModel(
            self.dataset, features=3, outputs=7, expand=True
        )

        self.yoc = int(model_specs["yoc"])  # year of construction
        # Check that year of construction is within the range 1600-2100
        if self.yoc < 1600 or self.yoc > 2100:
            raise ValueError("Year of construction must be within the range 1600-2100")

        self.heated_area = int(model_specs["heated_area"])  # heated living area [m2]
        # Check that heated area is within the range 10-1000
        if self.heated_area < 10 or self.heated_area > 1000:
            raise ValueError("Heated area must be within the range 10-1000")

        # Renovations:
        # Var1: original condition at construction of the building
        # Var2: conventional renovation with moderate insulation of the building shell and window replacement with two-panes glazing
        # Var3: deep renovation with high insulation and three-panes glazing
        self.renovation = int(model_specs["renovation"])  # state of renovation
        # Check that renovation is either 1, 2, or 3
        if self.renovation not in [1, 2, 3]:
            raise ValueError("Renovation must be 1, 2, or 3")

        self.heat_gain = 3.0 / 1e3  # internal heat gain, constant at 3 W/m2
        self.P_hgain = self.heated_area * self.heat_gain  # internal heat gain [kW]

        # Set the model parameters and annual net heat demand using linear regression model
        self.model.train_model(n_iterations=100, learning_rate=0.1)
        params = self.model.predict(
            np.array([[self.yoc, self.heated_area, self.renovation]]).astype(float)
        )
        params = params.flatten()  # first six elements are the parameters of the 3R2C model and last element is the annual heat demand
        # params = [2.92, 17.79, 2.14, 7.97, 16.03, 0.57] # Mean model parameters
        self.set_model_params(params)

        # Approximate annual net heat demand from linear regression model
        self.annual_net_heat_demand = params[-1] * self.heated_area  # [kWh/a]
        # TABULA: Warm water demand:
        # 10 kWh/(m2 a) for single-family houses
        # 15 kWh/(m2 a) for multi-family houses
        self.hot_water_demand = 10.0  # [kWh/m2/a]
        self.annual_net_heat_demand += (
            self.hot_water_demand * self.heated_area
        )  # [kWh/a]

        # Pre-calculate time constants
        self.dt = self.host.timebase / 3600
        self.timebase_sqrt = np.sqrt(self.host.timebase)

    def set_model_params(self, params):
        # Effective window area for absorption of solar gains on internal air [m2]
        self.Ai = params[0]

        # Capacitance of building envelope [kWh/K]
        self.Ce = params[1]

        # Capacitance of interior [kWh/K]
        self.Ci = params[2]

        # Thermal resistance between building envelope and the ambient [K/kW]
        self.Rea = params[3]

        # Thermal resistance between interior and the ambient [K/kW]
        self.Ria = params[4]

        # Thermal resistance between interior and building envelope [K/kW]
        self.Rie = params[5]

        if False:
            logger.info("Parameters of thermal 3R2C model:")
            logger.info(f"Ai: {self.Ai:.2f} (2.92)")
            logger.info(f"Ce: {self.Ce:.2f} (17.79)")
            logger.info(f"Ci: {self.Ci:.2f} (2.14)")
            logger.info(f"Rea: {self.Rea:.2f} (7.97)")
            logger.info(f"Ria: {self.Ria:.2f} (16.03)")
            logger.info(f"Rie: {self.Rie:.2f} (0.57)")
            logger.info("")

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
        ) * self.dt + np.random.normal() / self.timebase_sqrt
        dTe = (
            1.0 / (self.Ce * self.Rie) * (T_in - T_en)
            + 1.0 / (self.Ce * self.Rea) * (T_amb - T_en)
        ) * self.dt + np.random.normal() / self.timebase_sqrt

        # Update temperatures
        T_in += dTi
        T_en += dTe

        # NOTE: PFUSCH!!!
        # Safety: Prevent T_en from exceeding T_in
        if T_en > T_in:
            T_en = T_in - 2.0

        return T_in, T_en
