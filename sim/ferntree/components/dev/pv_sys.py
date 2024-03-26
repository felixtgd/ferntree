import logging

from dev import device


logger = logging.getLogger("ferntree")

class PVSys(device.Device):
    """Class for photovoltaic system."""

    def __init__(self, host, dev_specs):
        """Initializes a new instance of the PVSys class."""
        super().__init__(host)

        # Peak power of the PV system [kWp]
        if not dev_specs["peak_power"]:
            self.peak_power = 3000  # Default [kWp]
        else:
            self.peak_power = dev_specs["peak_power"]
        
        self.current_state = {"P_pv": 0.0}  # Current state of the PV system: Power output at current timestep [kW]

    def startup(self):
        """Startup of the pv system. """
        pass

    def timetick(self):
        """Simulates a single timestep of the PV system."""

        # Update current state of the PV system
        self.current_state["P_pv"] = self.peak_power * self.host.env_state.get("P_solar")
