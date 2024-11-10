import logging
from typing import Any, Union

from components.dev.baseload import BaseLoad
from components.dev.battery_dev import BatteryDev
from components.dev.device import Device
from components.dev.pv_sys import PVSys
from components.dev.smart_meter import SmartMeter
from components.host.sim_host import SimHost

logger = logging.getLogger("ferntree")


class SfHouse(Device):
    """Class for a single-family house.
    Each house has a baseload, a heating system, and optionally a PV system and battery.
    """

    def __init__(self, host: SimHost) -> None:
        """Initializes a new instance of the SfHouse class.
        - Adds the house to the host
        - Initializes the baseload, heating system, PV system, and battery.
        """
        super().__init__(host)

        self.host.add_house(self)
        self.components: dict[
            str, Union[Device, BaseLoad, PVSys, BatteryDev, SmartMeter]
        ]

    def add_component(self, comp: Device, name: str) -> None:
        """Adds a components to the house."""
        if isinstance(comp, Device):
            self.components[name] = comp
        else:
            raise TypeError("Can only add objects of class 'Device' to house.")

    def startup(self) -> None:
        """Startup of the house and its components."""
        for comp in self.components.values():
            comp.startup()

    def shutdown(self) -> None:
        """Shutdown of the house and its components."""
        for comp in self.components.values():
            comp.shutdown()

    def timetick(self) -> dict[str, Any]:
        """Simulates a single timestep of the house's components.
        First the baseload and the heating system are simulated to determine the
        electricity demand.
        Then the PV system is simulated to determine the electricity generation.
        Finally the battery is simulated to balance supply and demand.
        """
        for comp in self.components.values():
            comp.timetick()

        results: dict[str, Any] = self.get_results()

        return results

    def get_results(self) -> dict[str, Any]:
        """Returns the results of the house's components for the current timestep.
        The current state of each component is read from the smart meter and returned
        as a dictionary.
        These results are then converted to a ORM object and written to the database.
        """
        smart_meter = self.components.get("smart_meter")
        if not isinstance(smart_meter, SmartMeter):
            raise TypeError("Expected 'smart_meter' to be of type 'SmartMeter'")
        results: dict[str, Any] = smart_meter.get_measurements()

        return results
