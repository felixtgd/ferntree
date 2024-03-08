from dev import device


class HeatingDev(device.Device):
    """Class for a heating device. E.g. a heat pump.
    A heating device provides thermal heating power to a building and specifies electricity demand.
    """

    def __init__(self, host):
        """Initializes a new instance of the HeatingDev class."""
        super().__init__(host)

        self.P_heat_max = None
        self.cop = None

    def calc_electr_demand(self, P_heat_th):
        """Calculates the electrical heating power required to provide a given thermal heating power."""
        P_heat_el = P_heat_th / self.cop
        return P_heat_el