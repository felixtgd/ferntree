from dev import device

class HeatingCtrl(device.Device):
    """Class for a thermostat controller.
    This controller determines the required thermal heating power based on the current indoor temperature, the setpoint
    and the previous heating power. Using a variant of a PI-controller, the heating power is adjusted to maintain the
    indoor temperature close to the setpoint.
    """

    def __init__(self, host, ctrl_specs) -> None:
        """Initializes a new instance of the HeatingCtrl class."""

        super().__init__(host)

        self.temp_setpoint = ctrl_specs["temp_setpoint"]
        self.deadband = ctrl_specs["deadband"]

        self.lower_bound = self.temp_setpoint - self.deadband
        self.upper_bound = self.temp_setpoint + self.deadband

        self.ctrl_signal = 0.0
        self.integral = 0.0
        
    def set_ctrl_signal(self, T_in):
        """Determines the control signal to set the required thermal heating power based on the current indoor temperature.
        
        Args:
            T_in (float): Indoor temperature [K]

        Returns:
            float: The updated control signal for the heating system.
        """

        # Thermostat control of heating power
        if T_in < self.lower_bound:
            # If indoor temperature is below setpoint, turn on heating to maximum
            self.ctrl_signal = 1.0
            self.integral = 0.0
        elif T_in > self.upper_bound:
            # If indoor temperature is above setpoint, turn off heating
            self.ctrl_signal = 0.0
            self.integral = 0.0
        else:
            # Apply variant of a PI-controller to adjust heating power
            # Proportional term: error between setpoint and indoor temperature
            proportional = (self.temp_setpoint - T_in) / self.temp_setpoint
            # Integral term: sum of proportional errors over timesteps
            self.integral += proportional
            
            # Set new control signal
            self.ctrl_signal = min(max(0, (1 + proportional + self.integral)), 1)
        
        return self.ctrl_signal
