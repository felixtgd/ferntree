from dev import device


class HeatingDev(device.Device):
    """Class for a heating device. E.g. a heat pump.
    A heating device provides thermal heating power to a building and specifies electricity demand.
    """

    def __init__(self, host, dev_specs):
        """Initializes a new instance of the HeatingDev class."""
        super().__init__(host)

        self.type = dev_specs["type"]  # type of heating device, e.g. heat pump or boiler
        self.P_heat_th_max = dev_specs["P_heat_th_max"]  # maximum heating power of device [kW]
        
        if self.type == "heatpump":
            self.cop = dev_specs["cop"]
            
        try:
            self.efficiency = dev_specs["efficiency"]
        except KeyError:
            self.efficiency = 1.0
        
        # Initial thermal heating power in [kW]
        self.P_heat_th = self.P_heat_th_max 


    def set_heating_power(self, ctrl_signal):
        """Calculates the electrical heating power required to provide a given thermal heating power."""
        if ctrl_signal == 1.0:
            self.P_heat_th = self.P_heat_th_max
        else:
            self.P_heat_th = min(max(0, ctrl_signal * self.P_heat_th), self.P_heat_th_max)
        
        if self.type == "heatpump":
            P_heat_el = self.P_heat_th / self.cop
        else:
            P_heat_el = 0.0

        return self.P_heat_th, P_heat_el