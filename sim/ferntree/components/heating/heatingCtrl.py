from component import Component

class HeatingCtrl(Component):

    def __init__(self, temp_setpoint, deadband, P_heat_max) -> None:

        super().__init__()

        self.temp_setpoint = temp_setpoint
        self.deadband = deadband
        self.P_heat_max = P_heat_max
        
    def set_heating_power(self, T_in_prev, T_in_next, P_heat_prev):
        # Thermostat control of heating power
        if T_in_next < self.temp_setpoint - self.deadband:
            P_heat_next = self.P_heat_max
        elif T_in_next > self.temp_setpoint + self.deadband:
            P_heat_next = 0.0
        else:
            dTi = (T_in_prev - T_in_next) / T_in_prev # sweetspot: *100
            Ph_hat = (1 + dTi) * P_heat_prev
            P_heat_next = min(max(0, Ph_hat), self.P_heat_max)
        
        return P_heat_next
