import json

from components.component import Component
from database.database import Database
from database.orm_models import Timestep

class SimHost():
    def __init__(self) -> None:
        
        self.components = []

        self.timebase = None
        self.timesteps = None
        self.startTime = None
        self.currentTimestep = None

        self.batch_size = 1000
        self.data_buffer = []

        self.env_state = {}

    def startup(self):
        self.db = Database()
        self.db.startup()

        self.load_weather_data()

    def add_component(self, comp: Component) -> None:
        if comp.isinstance(Component):
            self.components.append(comp)
            comp.host = self
        else:
            raise TypeError("Can only add Components to simHost.")

    def load_weather_data(self):
        with open("example_input_data.json") as json_file:
            input_data = json.load(json_file)
            hourly_data = input_data["outputs"]["hourly"]

            self.T_amb = []
            self.P_solar = []

            for hd in hourly_data:
                self.T_amb.append(hd["T2m"] + 273.15) # [K]
                self.P_solar.append(hd["Gb(i)"] /1e3) # [kW/m2]
            
            self.timesteps = int(len(self.T_amb))

    def run_simulation(self):
        self.startup()

        for t in range(self.timesteps):
            self.timetick(t)

            if t%100 == 0:
                print(f"Timestep {self.currentTimestep}: T_amb = {self.T_amb[t]:.2f}, P_solar = {self.P_solar[t]:.2f}")
        
        if self.data_buffer:
            self.db.write_batch_to_db(self.data_buffer)

        self.shutdown()
        
    def timetick(self, t):
        self.updateState(t)
        self.currentTimestep = t
        
        for comp in self.components:
            comp.timetick()

        self.save_results()
        
    def updateState(self, t):
        self.env_state = {"t": t,
                          "T_amb": self.T_amb[t],
                          "P_solar": self.P_solar[t],
                          }


    def save_results(self):
        data = Timestep(
            timestep = self.currentTimestep,
            T_amb = self.T_amb[self.currentTimestep],
            P_solar = self.P_solar[self.currentTimestep],
            T_in = 0.0,
            T_en = 0.0,
            P_heat_th = 0.0,
            P_heat_el = 0.0,
            P_hgain = 0.0,
            P_base = 0.0,
            P_pv = 0.0,
            P_bat = 0.0,
        )
        
        self.data_buffer.append(data)

        if len(self.data_buffer) == self.batch_size:
            self.db.write_batch_to_db(self.data_buffer)
            self.data_buffer = []

    def shutdown(self):
        self.db.shutdown()



    