from dev import device
from database import orm_models


class SfHouse(device.Device):
    """Class for a single-family house.
    Each house has a baseload, a heating system, and optionally a PV system and a battery.
    """

    def __init__(self, host):
        """Initializes a new instance of the SfHouse class.
        - Adds the house to the host
        - Initializes the baseload, heating system, PV system, and battery
        """
        super().__init__(host)

        self.host.add_house(self)
        self.components = {}

    def add_component(self, comp: device.Device, name: str):
        """ Adds a components to the house. """
        if isinstance(comp, device.Device):
            self.components[name] = comp
        else:
            raise TypeError("Can only add objects of class 'Device' to house.")

    def startup(self):
        """Startup of the house and its components."""
        for comp in self.components.values():
            comp.startup()

    def shutdown(self):
        """Shutdown of the house and its components."""
        for comp in self.components.values():
            comp.shutdown()

    def timetick(self):
        """Simulates a single timestep of the house's components.
        First the baseload and the heating system are simulated to determine the electricity demand.
        Then the PV system is simulated to determine the electricity generation.
        Finally the battery is simulated to balance supply and demand.
        """
        for comp in self.components.values():
            comp.timetick()

        results = self.get_results()

        return results

    def get_results(self):
        """Returns the results of the house's components for the current timestep.
        The current state of each component is read and returned as a Timestep object.
        These results are then written to the database.
        """
        results = orm_models.Timestep(
            time=self.host.env_state.get("time"),
            T_amb=self.host.env_state.get("T_amb"),
            P_solar=self.host.env_state.get("P_solar"),
            T_in=self.components.get("heating").current_state.get("T_in"),
            T_en=self.components.get("heating").current_state.get("T_en"),
            P_heat_th=self.components.get("heating").current_state.get("P_heat_th"),
            P_heat_el=self.components.get("heating").current_state.get("P_heat_el"),
            P_base=0.0,
            P_pv=0.0,
            P_bat=0.0,
        )
        return results
