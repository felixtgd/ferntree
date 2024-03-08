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

        self.baseload = None
        self.heating_sys = None
        self.pv = None
        self.battery = None

    def startup(self):
        """Startup of the house and its components."""
        # self.baseload.startup()
        self.heating_sys.startup()
        # self.pv.startup()
        # self.battery.startup()

    def shutdown(self):
        """Shutdown of the house and its components."""
        pass

    def timetick(self):
        """Simulates a single timestep of the house's components.
        First the baseload and the heating system are simulated to determine the electricity demand.
        Then the PV system is simulated to determine the electricity generation.
        Finally the battery is simulated to balance supply and demand.
        """
        # self.baseload.timetick()
        self.heating_sys.timetick()
        # self.pv.timetick()
        # self.battery.timetick()

        results = self.get_results()

        return results

    def get_results(self):
        """Returns the results of the house's components for the current timestep.
        The current state of each component is read and returned as a Timestep object.
        These results are then written to the database.
        """
        results = orm_models.Timestep(
            time=self.host.env_state["time"],
            T_amb=self.host.env_state["T_amb"],
            P_solar=self.host.env_state["P_solar"],
            T_in=self.heating_sys.current_state["T_in"],
            T_en=self.heating_sys.current_state["T_en"],
            P_heat_th=self.heating_sys.current_state["P_heat_th"],
            P_heat_el=self.heating_sys.current_state["P_heat_el"],
            P_hgain=self.heating_sys.current_state["P_hgain"],
            P_base=0.0,
            P_pv=0.0,
            P_bat=0.0,
        )
        return results
