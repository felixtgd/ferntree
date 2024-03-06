import json
import os
from pytz import timezone
from datetime import datetime

from host import sim_host
from dev import sf_house
from dev import heating

# Load settings from settings.json
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")) as json_file:
    settings = json.load(json_file)

# Set up simulation
sim = sim_host.SimHost()
sim.timebase = int(settings["sim"]["timebase"])
sim.timesteps = int(365 * 24 * 3600 / sim.timebase)

timeZone = timezone(settings["sim"]["timezone"])
sim.start_time = int(timeZone.localize(datetime(2019, 1, 1)).timestamp())

## DEFINE MODEL

# 1. Define a house
house = sf_house.SfHouse(sim)

# 2. Define the baseload and add it to the house
# baseload = Baseload(sim)
# house.baseload = baseload

# 3. Define the heating system and add it to the house
heating_sys = heating.HeatingSys(sim)

heating_sys.thermal_model = settings["thermal"]["thermal_model"]
heating_sys.temp_setpoint = settings["thermal"]["temp_setpoint"] + 273.15 # in Kelvin
heating_sys.deadband =      settings["thermal"]["deadband"]
heating_sys.P_heat_max =    settings["thermal"]["P_heat_max"]
heating_sys.heated_area =   settings["thermal"]["heated_area"]

house.heating_sys = heating_sys

# # 4. Define the PV system and add it to the house
# pv = PV(sim)
# pv.size = settings["pv_size"]
# pv.efficiency = settings["pv_efficiency"]
# house.pv = pv

# # 5. Define the battery and add it to the house
# battery = Battery(sim)
# battery.capacity = settings["battery_capacity"]
# battery.P_bat_max = settings["P_bat_max"]
# house.battery = battery


# Start the simulation
sim.run_simulation()

