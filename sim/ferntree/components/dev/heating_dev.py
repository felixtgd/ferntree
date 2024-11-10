from typing import Any

from components.dev.device import Device
from components.host.sim_host import SimHost


class HeatingDev(Device):
    """Class for a heating device. E.g. a heat pump.
    A heating device provides thermal heating power to a building and
    specifies electricity demand.
    """

    def __init__(self, host: SimHost, dev_specs: dict[str, Any]) -> None:
        """Initializes a new instance of the HeatingDev class."""
        super().__init__(host)

        self.type: str = dev_specs[
            "type"
        ]  # type of heating device, e.g. heat pump or boiler
        self.P_heat_th_max: float = dev_specs[
            "P_heat_th_max"
        ]  # maximum heating power of device [kW]

        if self.type == "heatpump":
            self.cop: float = dev_specs["cop"]

        try:
            self.efficiency: float = dev_specs["efficiency"]
        except KeyError:
            self.efficiency = 1.0

        # Initial thermal heating power in [kW]
        self.P_heat_th: float = self.P_heat_th_max

    def set_thermal_heating_power(self, ctrl_signal: float) -> float:
        """Calculates the electrical heating power required to provide a given
        thermal heating power.

        Args:
            ctrl_signal (float): Control signal for the heating device.

        """
        if ctrl_signal == -1.0:
            self.P_heat_th = self.P_heat_th_max
        else:
            self.P_heat_th = min(
                max(0, ctrl_signal * self.P_heat_th), self.P_heat_th_max
            )

        return self.P_heat_th

    def set_electrical_heating_power(self, P_heat_th: float) -> float:
        """Sets the electrical heating power of the heating device.

        Args:
            P_heat_th (float): Thermal heating power [kW]

        Returns:
            float: Electrical heating power [kW]

        """
        if self.type == "heatpump":
            P_heat_el = P_heat_th / self.cop
        else:
            P_heat_el = 0.0

        return P_heat_el
