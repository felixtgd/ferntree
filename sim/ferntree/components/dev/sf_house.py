from dev import device
from database import orm_models

class SfHouse(device.Device):

    def __init__(self, host) -> None:
        super().__init__(host)

        self.host = host
        self.host.add_house(self)

        self.baseload =     None
        self.heating_sys =  None
        self.pv =           None
        self.battery =      None

    def startup(self):
        # self.baseload.startup()
        self.heating_sys.startup()
        # self.pv.startup()
        # self.battery.startup()

    def timetick(self):
        # self.baseload.timetick()
        self.heating_sys.timetick()
        # self.pv.timetick()
        # self.battery.timetick()

        return self.get_results()


    def get_results(self):
        results = orm_models.Timestep(
            timestep =  self.host.env_state["time"],
            T_amb =     self.host.env_state["T_amb"],
            P_solar =   self.host.env_state["P_solar"],
            T_in =      self.heating_sys.current_state["T_in"],
            T_en =      self.heating_sys.current_state["T_en"],
            P_heat_th = self.heating_sys.current_state["P_heat_th"],
            P_heat_el = 0.0,
            P_hgain =   self.heating_sys.current_state["P_hgain"],
            P_base =    0.0,
            P_pv =      0.0,
            P_bat =     0.0,
        )
        return results



