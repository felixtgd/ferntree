import logging

from components.dev.device import Device
from components.host.sim_host import SimHost

logger: logging.Logger = logging.getLogger("ferntree")


class PVSys(Device):  # type: ignore[misc]
    """Class for photovoltaic system."""

    def __init__(self, host: SimHost, dev_specs: dict[str, float]) -> None:
        """Initializes a new instance of the PVSys class."""
        super().__init__(host)

        # Peak power of the PV system [kWp]
        if not dev_specs["peak_power"]:
            self.peak_power: float = 0.0  # Default [kWp]
        else:
            self.peak_power = dev_specs["peak_power"]

        self.current_state: dict[str, float] = {
            "P_pv": 0.0
        }  # Current state of the PV system: Power output at current timestep [kW]

    def startup(self) -> None:
        """Startup of the pv system."""
        pass

    def timetick(self) -> None:
        """Simulates a single timestep of the PV system."""
        # Update current state of the PV system
        # Convention: Generation is negative, consumption positive
        P_solar: float = self.host.env_state.get("P_solar") or 0.0
        self.current_state["P_pv"] = -1 * self.peak_power * P_solar * 1e-3
