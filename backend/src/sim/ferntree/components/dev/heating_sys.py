import logging

from components.ctrl.heating_ctrl import HeatingCtrl
from components.dev.device import Device
from components.dev.heating_dev import HeatingDev
from components.host.sim_host import SimHost
from components.models.thermal_model import ThermalModel

logger: logging.Logger = logging.getLogger("ferntree")


class HeatingSys(Device):  # type: ignore[misc]
    """Class for a heating system.
    A heating system consists of a thermostat controller, a thermal building model
    and a heating device.
    Thermostat controller: determines required thermal heating power based on current
    temperature and setpoint.
    Thermal building model: computes thermal response of building to heating power and
    ambient temperature.
    Heating device: provides thermal heating power to building and specifies
    electricity demand.
    """

    def __init__(self, host: SimHost) -> None:
        """Initializes a new instance of the HeatingSys class."""
        super().__init__(host)

        # Components of heating system
        self.thermal_model: ThermalModel  # thermal building model
        self.heating_ctrl: HeatingCtrl  # thermostat controller
        self.heating_dev: HeatingDev  # heating device, e.g. heat pump

        # Initialize current state of the heating system
        self.current_state: dict[str, float] = {
            "T_in": 20.0 + 273.15,  # indoor temperature in [K]
            "T_en": 5.0 + 273.15,  # building envelope temperature in [K]
            "P_heat_th": 0.0,  # thermal heating power in [kW]
            "P_heat_el": 0.0,  # electrical heating power in [kW]
        }

        # Initialize heat demand profiles
        self.heat_demand_profiles: dict[str, list[float]] = {
            "T_in": [self.current_state["T_in"]],  # indoor temperature in [K]
            "T_en": [
                self.current_state["T_en"]
            ],  # building envelope temperature in [K]
            "P_heat_th": [
                self.current_state["P_heat_th"]
            ],  # thermal heating power in [kW]
        }

    def startup(self) -> None:
        """Startup of the heating system.
        - Initializes thermostat controller, thermal building model and heating device
        - Creates heat demand profiles and scales to annual demand.
        """
        # Create heat demand profiles and scale to annual demand
        self.create_heat_demand_profiles()

    def create_heat_demand_profiles(self) -> None:
        """Creates heat demand profiles for the heating system and scales to
        annual demand.
        - Simulates thermal behaviour and heating demand of building
        - Scales to annual demand as defined in user input or approximated from
        LinReg model.
        """
        # First: simulate thermal behaviour and heating demand of building
        for t in range(self.host.timesteps):
            # Get state variables of current timestep from simHost
            T_amb: float = self.host.T_amb[t]
            P_solar: float = self.host.P_solar[t]

            # Get state variables of previous timestep from heating system
            T_in: float = self.heat_demand_profiles["T_in"][t]
            T_en: float = self.heat_demand_profiles["T_en"][t]

            # Heating controller: Determine control signal for heating device based on
            # thermal response of building
            ctrl_signal: float = self.heating_ctrl.set_ctrl_signal(T_in)

            # Heating device: Calculate heating power (th and el) of heating system
            # based on control signal
            P_heat_th_next: float = self.heating_dev.set_thermal_heating_power(
                ctrl_signal
            )

            # Thermal model: Compute thermal response of building
            T_in_next, T_en_next = self.thermal_model.compute_thermal_response(
                T_in, T_en, T_amb, P_solar, P_heat_th_next
            )

            # Update current state of heating system
            self.heat_demand_profiles["T_in"].append(T_in_next)
            self.heat_demand_profiles["T_en"].append(T_en_next)
            self.heat_demand_profiles["P_heat_th"].append(P_heat_th_next)

        # Second: scale to annual demand as defined in user input or approximated
        # from LinReg model
        annual_net_heat_demand: float = self.thermal_model.annual_net_heat_demand
        total_P_heat_th: float = sum(self.heat_demand_profiles["P_heat_th"])
        scaling_factor: float = annual_net_heat_demand / total_P_heat_th
        logger.info(
            f"Annual net heat demand (model): {annual_net_heat_demand/self.thermal_model.heated_area:.2f} kWh/m2/a"  # noqa: E501
        )
        logger.info(
            f"Total heating demand (sim): {total_P_heat_th/self.thermal_model.heated_area:.2f} kWh/m2/a"  # noqa: E501
        )
        logger.info(f"Scaling factor for heat demand profile: {scaling_factor:.2f}")
        self.heat_demand_profiles["P_heat_th"] = [
            val * scaling_factor for val in self.heat_demand_profiles["P_heat_th"]
        ]

    def timetick(self) -> None:
        """Simulates a single timestep of the heating system."""
        # Get current timestep from simHost
        t: int = self.host.current_timestep

        # Update current state of heating system
        self.current_state["T_in"] = self.heat_demand_profiles["T_in"][t]
        self.current_state["T_en"] = self.heat_demand_profiles["T_en"][t]
        self.current_state["P_heat_th"] = self.heat_demand_profiles["P_heat_th"][t]

        # Determine electrical heating power based on thermal heating power
        self.current_state["P_heat_el"] = self.heating_dev.set_electrical_heating_power(
            self.current_state["P_heat_th"]
        )
