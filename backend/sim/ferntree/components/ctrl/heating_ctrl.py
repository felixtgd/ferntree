from typing import Any

from components.dev.device import Device
from components.host.sim_host import SimHost


class HeatingCtrl(Device):  # type: ignore[misc]
    """Class for a thermostat controller.
    This controller determines the control signal for setting required thermal heating
    power based on the current indoor temperature and the setpoint. Using a variant of
    a PI-controller, the heating power is adjusted to maintain the indoor temperature
    close to the setpoint.
    """

    def __init__(self, host: SimHost, ctrl_specs: dict[str, Any]) -> None:
        """Initializes a new instance of the HeatingCtrl class."""
        super().__init__(host)

        self.temp_setpoint: float = (
            ctrl_specs["temp_setpoint"] + 273.15
        )  # temperature setpoint in [K]
        self.deadband: float = ctrl_specs["deadband"]  # deadband around setpoint

        self.lower_bound: float = self.temp_setpoint - self.deadband
        self.upper_bound: float = self.temp_setpoint + self.deadband

        self.integral: float = 0.0  # integral term of the PI-controller

    def set_ctrl_signal(self, T_in: float) -> float:
        """Determines the control signal to set the required thermal heating power based
        on the current indoor temperature.

        Args:
            T_in (float): Indoor temperature [K]

        Returns:
            float: The updated control signal for the heating system.

        """
        # Thermostat control of heating power
        if T_in < self.lower_bound:
            # If indoor temperature is below setpoint, turn on heating to maximum
            ctrl_signal: float = -1.0
            self.integral = 0.0
        elif T_in > self.upper_bound:
            # If indoor temperature is above setpoint, turn off heating
            ctrl_signal = 0.0
            self.integral = 0.0
        else:
            # Apply variant of a PI-controller to adjust heating power
            # Proportional term: error between setpoint and indoor temperature
            proportional: float = (self.temp_setpoint - T_in) / self.temp_setpoint
            # Integral term: sum of proportional errors over timesteps
            self.integral += proportional

            # Set new control signal
            ctrl_signal = max(0, (1 + proportional + self.integral))

        return ctrl_signal
