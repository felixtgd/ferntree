import logging
from typing import Optional, Union

from components.dev.device import Device
from components.dev.sf_house import SfHouse
from components.host.sim_host import SimHost

logger: logging.Logger = logging.getLogger("ferntree")


class SmartMeter(Device):
    """Class for a house smart meter."""

    def __init__(self, host: SimHost, house: SfHouse) -> None:
        """Initializes a new instance of the SmartMeter class."""
        super().__init__(host)

        # House object being monitored
        self.house: SfHouse = house

        self.measurements: dict[str, Optional[Union[float, int]]] = {
            "time": 0.0,  # Time of the simulation
            "T_amb": 0.0,  # Ambient temperature [K]
            "P_solar": 0.0,  # Solar irradiance [kW/m2]
            # "T_in": 0.0,  # Indoor temperature [K]
            # "T_en": 0.0,  # Building envelope temperature [K]
            # "P_heat_th": 0.0,  # Thermal heating power [kW]
            # "P_heat_el": 0.0,  # Electrical heating power [kW]
            "P_base": 0.0,  # Baseload power [kW]
            "P_pv": 0.0,  # PV power generation [kW]
            "P_bat": 0.0,  # Battery power [kW]
            "Soc_bat": 0.0,  # State of charge of battery [kWh]
            "fill_level": 0.0,  # Fill level of battery [0 ... 1]
            "P_load_pred": 0.0,  # Predicted net load of house [kW]
        }

    def startup(self) -> None:
        """Startup of the smart meter."""
        # self.update_measurements()
        self.baseload: Optional[Device] = self.house.components.get("baseload")
        self.pv: Optional[Device] = self.house.components.get("pv")
        self.battery: Optional[Device] = self.house.components.get("battery")

    def timetick(self) -> None:
        """Simulates a single timestep of the smart meter."""
        # self.update_measurements()
        pass

    def update_measurements(self) -> None:
        """Updates the measurements of the smart meter."""
        self.measurements = {
            "time": self.host.env_state.get("time"),
            "T_amb": self.host.env_state.get("T_amb"),
            "P_solar": self.host.env_state.get("P_solar"),
            # # Inside temperature
            # "T_in": 0.0
            # if self.house.components.get("heating") is None
            # else self.house.components.get("heating").current_state.get("T_in"),
            # # Building envelope temperature
            # "T_en": 0.0
            # if self.house.components.get("heating") is None
            # else self.house.components.get("heating").current_state.get("T_en"),
            # # Thermal heating demand
            # "P_heat_th": 0.0
            # if self.house.components.get("heating") is None
            # else self.house.components.get("heating").current_state.get("P_heat_th"),
            # # Electrical heating demand
            # "P_heat_el": 0.0
            # if self.house.components.get("heating") is None
            # else self.house.components.get("heating").current_state.get("P_heat_el"),
            # Baseload power
            "P_base": 0.0
            if self.baseload is None
            else self.baseload.current_state.get("P_base"),
            # PV power generation
            "P_pv": 0.0 if self.pv is None else self.pv.current_state.get("P_pv"),
            # Battery power
            "P_bat": 0.0
            if self.battery is None
            else self.battery.current_state.get("P_bat"),
            # Battery state of charge
            "Soc_bat": 0.0
            if self.battery is None
            else self.battery.current_state.get("Soc_bat"),
            # Battery fill level
            "fill_level": 0.0
            if self.battery is None
            else self.battery.current_state.get("fill_level"),
            # Predicted net load of house
            "P_load_pred": 0.0
            if self.battery is None
            else self.battery.current_state.get("P_load_pred"),
        }

    def get_net_load(self) -> float:
        """Returns the net load of the house."""
        self.update_measurements()
        P_base: float = float(self.measurements.get("P_base") or 0.0)
        P_pv: float = float(self.measurements.get("P_pv") or 0.0)

        P_net_load: float = P_base + P_pv

        return P_net_load

    def get_measurements(self) -> dict[str, Optional[Union[float, int]]]:
        """Returns all measurements of the house."""
        self.update_measurements()
        return self.measurements
