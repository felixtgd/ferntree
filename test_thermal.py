import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json

# SFH F Var3 Model parameters
Ai = 1.72
Ce = 16.39
Ci = 2.02
Rea = 13.26
Ria = 24.38
Rie = 0.53

# Inputs
with open("example_input_data.json") as json_file:
    input_data = json.load(json_file)
    hourly_data = pd.DataFrame(input_data["outputs"]["hourly"])
    Ta = np.array(hourly_data["T2m"]) + 273.15 # [K]
    Ps = np.array(hourly_data["Gb(i)"]) /1e3 # [kW/m2]

# Simulation parameters
timesteps = len(Ta)

Pheat_max = 3.9 # [kW]

heated_area = 158 # heated living area [m2]
Pg = np.ones(len(Ta)) * 3/1e3 * heated_area # internal heat gains constant at 3 W/m2

temp_setpoint = 20 + 273.15 # temperature setpoint for heating [k]
deadband = 1 # deadband around setpoint

# Initialisation of observation variables
Ti, Te, Ph = np.zeros(timesteps), np.zeros(timesteps), np.zeros(timesteps)
Ti[0], Te[0] = Ta[0], Ta[0] 

timestamp = pd.date_range(start="2019-01-01", periods=len(Ti), freq="H")
sim_data_df = pd.DataFrame(index = pd.to_datetime(timestamp, format="%Y%m%d:%H%M"),
                           data = {"Ti": Ti,
                                   "Te": Te,
                                   "Ta": Ta,
                                   "Ps": Ps,
                                   "Ph": Ph,
                                   "Pg": Pg})

sim_data_df.resample("5min").interpolate()

Te = sim_data_df["Te"]
Ta = sim_data_df["Ta"]
Ti = sim_data_df["Ti"]

Ph = sim_data_df["Ph"]
Pg = sim_data_df["Pg"]
Ps = sim_data_df["Ps"]

for t in range(timesteps-1):
    # Thermal RC-model of building 
    dTi = (1.0/(Ci * Rie) * (Te[t] - Ti[t]) + 1.0/(Ci * Ria) * (Ta[t] - Ti[t]) + Ai / Ci * Ps[t] + 1.0/Ci * (Ph[t] + Pg[t])) # + si * dwi
    dTe = (1.0/(Ce * Rie) * (Ti[t] - Te[t]) + 1.0/(Ce * Rea) * (Ta[t] - Te[t])) # + si * dwi
    
    # Update temperatures
    Ti[t+1] = Ti[t]+dTi
    Te[t+1] = Te[t]+dTe

    # Thermostat control of heating power
    if Ti[t+1] < temp_setpoint - deadband:
        Ph[t+1] = Pheat_max
    elif Ti[t+1] > temp_setpoint + deadband:
        Ph[t+1] = 0.0
    else:
        dPh = (temp_setpoint - Ti[t+1]) / Ti[t+1] * Ph[t]
        Ph[t+1] = Ph[t] + dPh

sim_data_df["Te"] = Te
sim_data_df["Ta"] = Ta
sim_data_df["Ti"] = Ti

sim_data_df["Ph"] = Ph
sim_data_df["Pg"] = Pg
sim_data_df["Ps"] = Ps

f, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(sim_data_df["Ti"][100:200], label="Ti")
ax1.plot(sim_data_df["Te"][100:200], label="Te")
ax1.plot(sim_data_df["Ta"][100:200], label="Ta")
ax1.legend()
ax1.grid()

ax2.plot(sim_data_df["Ps"][100:200], label="Ps")
ax2.plot(sim_data_df["Ph"][100:200], label="Ph")
ax2.plot(sim_data_df["Pg"][100:200], label="Pg")
ax2.legend()
ax2.grid()
