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
        

    def set_heating_power(self, ctrl_signal):
        """Calculates the electrical heating power required to provide a given thermal heating power."""
        P_heat_th = ctrl_signal * self.P_heat_th_max #NOTE: test if P_max works, else change to previous P and keep track of P

        if self.type == "heatpump":
            P_heat_el = P_heat_th / self.cop
        else:
            P_heat_el = 0.0

        return P_heat_th, P_heat_el