import json

from dev import sf_house
from database import database

class SimHost():
    def __init__(self) -> None:
        
        self.timebase =     None
        self.timesteps =    None
        self.start_time =   None
        self.current_time = None

        self.house = None

        self.env_state = {
            "time":     None,
            "T_amb":    None,
            "P_solar":  None,
            }

    def startup(self):
        self.current_time = self.start_time

        self.db = database.Database()
        self.db.startup()

        self.house.startup()

        self.load_weather_data()
    
    def shutdown(self):
        self.db.shutdown()

    def add_house(self, house: sf_house.SfHouse) -> None:
        if isinstance(house, sf_house.SfHouse):
            self.house = house
        else:
            raise TypeError("Can only add objects of class 'House' to simHost.")

    def run_simulation(self):
        self.startup()

        for t in range(self.timesteps):
            self.timetick(t)
            if t%100 == 0:
                print(f"Timestep {t}: T_amb = {self.T_amb[t]:.2f}, P_solar = {self.P_solar[t]:.2f}")
        
        self.shutdown()
        
    def timetick(self, t):
        self.updateState(t)
        
        results = self.house.timetick()

        self.save_results(results)

        self.current_time += self.timebase
        
    def updateState(self, t):
        self.env_state = {"time": self.current_time,
                          "T_amb": self.T_amb[t],
                          "P_solar": self.P_solar[t],
                          }


    def save_results(self, results):
        self.db.write_data_to_db(results)


    # Only for prototyping, will be replaced by database access
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

    