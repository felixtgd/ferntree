import logging

from components.ctrl.battery_ctrl import BatteryCtrl
from components.dev.device import Device
from components.host.sim_host import SimHost

logger: logging.Logger = logging.getLogger("ferntree")


class BatteryDev(Device):
    """Class for battery energy storage."""

    def __init__(self, host: SimHost, dev_specs: dict[str, float]) -> None:
        """Initializes a new instance of the BatteryDev class."""
        super().__init__(host)

        # Capacity of the battery [kWh]
        self.capacity: float = dev_specs["capacity"]
        # Maximum charging/discharging power of the battery [kW]
        self.max_power: float = dev_specs["max_power"]
        # Initial state of charge [kWh]
        self.soc_init: float = dev_specs["soc_init"]

        # Battery controller (is set by simBuilder)
        self.battery_ctrl: BatteryCtrl

        # Current state of the battery
        self.current_state: dict[str, float] = {
            "P_bat": 0.0,  # Power at current timestep [kW]
            "Soc_bat": self.soc_init,  # State of charge at current timestep [kWh]
            "fill_level": 0.0,  # Fill level of battery [0 ... 1]
            "P_load_pred": 0.0,  # Predicted load of house at current timestep [kW]
        }

    def startup(self) -> None:
        """Startup of the battery."""
        pass

    def timetick(self) -> None:
        """Simulates a single timestep of the battery."""
        # Update current state of the battery
        # Convention: Generation is negative, consumption positive
        bat_pwr, soc_t, Z_t, P_load_pred = self.battery_ctrl.set_battery_power(
            self.current_state["Soc_bat"], self.max_power, self.capacity
        )
        self.current_state["P_bat"] = bat_pwr
        self.current_state["Soc_bat"] = soc_t
        self.current_state["fill_level"] = Z_t
        self.current_state["P_load_pred"] = P_load_pred
