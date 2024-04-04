from components.component import Component


class HeatingCtrl(Component):
    def __init__(self, temp_setpoint, deadband, P_heat_max) -> None:
        super().__init__()

        self.temp_setpoint = temp_setpoint
        self.deadband = deadband
        self.P_heat_max = P_heat_max

        self.error_int = 0

    def set_heating_power(self, T_in, P_heat_th):
        # Thermostat control of heating power
        if T_in < self.temp_setpoint - self.deadband:
            P_heat_th_next = self.P_heat_max
            self.error_int = 0
        elif T_in > self.temp_setpoint + self.deadband:
            P_heat_th_next = 0.0
            self.error_int = 0
        else:
            # Variant of a PI-controller
            # Proportional term
            self.error_prop = (self.temp_setpoint - T_in) / self.temp_setpoint
            # Integral term
            self.error_int += self.error_prop

            Ph_hat = (1 + self.error_prop + self.error_int) * P_heat_th
            P_heat_th_next = min(max(0, Ph_hat), self.P_heat_max)

        return P_heat_th_next
