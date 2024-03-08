from dev import device

class HeatingCtrl(device.Device):
    """Class for a thermostat controller.
    This controller determines the required thermal heating power based on the current indoor temperature, the setpoint
    and the previous heating power. Using a variant of a PI-controller, the heating power is adjusted to maintain the
    indoor temperature close to the setpoint.
    """

    def __init__(self, host) -> None:
        """Initializes a new instance of the HeatingCtrl class."""

        super().__init__(host)

        self.temp_setpoint = None
        self.deadband = None
        self.P_heat_max = None

        self.integral = 0.0
        
    def set_heating_power(self, T_in, P_heat_th):
        """Determines the required thermal heating power based on the current indoor temperature and the previous heating power.
        
        Args:
            T_in (float): Indoor temperature [K]
            P_heat_th (float): Previous thermal heating power [kW]

        Returns:
            float: The updated thermal heating power [kW]
        """

        lower_bound = self.temp_setpoint - self.deadband
        upper_bound = self.temp_setpoint + self.deadband
        
        # Thermostat control of heating power
        if T_in < lower_bound:
            # If indoor temperature is below setpoint, turn on heating to maximum
            P_heat_th_next = self.P_heat_max
            self.integral = 0.0
        elif T_in > upper_bound:
            # If indoor temperature is above setpoint, turn off heating
            P_heat_th_next = 0.0
            self.integral = 0.0
        else:
            # Apply variant of a PI-controller to adjust heating power
            # Proportional term: error between setpoint and indoor temperature
            proportional = (self.temp_setpoint - T_in) / self.temp_setpoint
            # Integral term: sum of proportional errors over timesteps
            self.integral += proportional
            
            Ph_hat = (1 + proportional + self.integral) * P_heat_th
            P_heat_th_next = min(max(0, Ph_hat), self.P_heat_max)
        
        return P_heat_th_next
