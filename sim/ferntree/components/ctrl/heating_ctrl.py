from dev import device

class HeatingCtrl(device.Device):

    def __init__(self, host, temp_setpoint, deadband, P_heat_max) -> None:

        super().__init__(host)

        self.temp_setpoint = temp_setpoint
        self.deadband = deadband
        self.P_heat_max = P_heat_max

        self.integral = 0.0
        
    def set_heating_power(self, T_in, P_heat_th):
        # Thermostat control of heating power
        if T_in < self.temp_setpoint - self.deadband:
            # If inside temperature is below setpoint, turn on heating to maximum
            P_heat_th_next = self.P_heat_max
            self.integral = 0.0
        elif T_in > self.temp_setpoint + self.deadband:
            # If inside temperature is above setpoint, turn off heating
            P_heat_th_next = 0.0
            self.integral = 0.0
        else:
            # Apply variant of a PI-controller to adjust heating power
            # Proportional term: error between setpoint and inside temperature
            self.proportional = (self.temp_setpoint - T_in) / self.temp_setpoint
            # Integral term: sum of proportional errors over timesteps
            self.integral += self.proportional
            
            Ph_hat = (1 + self.proportional + self.integral) * P_heat_th
            P_heat_th_next = min(max(0, Ph_hat), self.P_heat_max)
        
        return P_heat_th_next
