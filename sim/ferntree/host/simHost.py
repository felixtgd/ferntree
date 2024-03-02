import json

from components.component import Component
from database.database import Database

class SimHost():
    def __init__(self) -> None:
        
        self.components = []

        self.timebase = None
        self.timesteps = None
        self.startTime = None
        self.currentTimestep = None

        self.startup()

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

            self.ambient_temp = []
            self.solar_irradiance = []

            for hd in hourly_data:
                self.ambient_temp.append(hd["T2m"] + 273.15) # [K]
                self.solar_irradiance.append(hd["Gb(i)"] /1e3) # [kW/m2]
            
            self.timesteps = int(len(self.ambient_temp))

    def start_simulation(self):
        for t in range(self.timesteps):
            self.timetick(t)

            if t%100 == 0:
                print(f"Timestep {self.currentTimestep}: T_amb = {self.ambient_temp[t]:.2f}, P_solar = {self.solar_irradiance[t]:.2f}")
        
        self.shutdown()
        
    def timetick(self, t):
        self.currentTimestep = t
        self.write_to_db()
        
    def write_to_db(self):
        data = {
            "timestep": self.currentTimestep,
            "T_amb": self.ambient_temp[self.currentTimestep],
            "P_solar": self.solar_irradiance[self.currentTimestep],
            "T_in": 0.0,
            "T_env": 0.0,
            "P_heat_th": 0.0,
            "P_heat_el": 0.0,
            "P_hgain": 0.0,
            "P_base": 0.0,
            "P_pv": 0.0,
            "P_bat": 0.0,
            }
        
        self.db.write_data(data)
    
    def shutdown(self):
        self.db.shutdown()



    