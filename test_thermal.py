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
timebase = 60*60 # seconds

Pheat_max = 3.9 # [kW]

heated_area = 158 # heated living area [m2]
Pg = np.ones(len(Ta)) * 3/1e3 * heated_area # internal heat gains constant at 3 W/m2

temp_setpoint = 20 + 273.15 # temperature setpoint for heating [k]
deadband = 1 # deadband around setpoint

# Initialisation of observation variables
Ti, Te, Ph = np.zeros(timesteps), np.zeros(timesteps), np.zeros(timesteps)
Ti[0], Te[0] = temp_setpoint, temp_setpoint# Ta[0], Ta[0] 

error_int = 0
error = []
time = []

for t in range(timesteps-1):
    # # Thermal RC-model of building 
    # dTi = (1.0/(Ci * Rie) * (Te[t] - Ti[t]) + 1.0/(Ci * Ria) * (Ta[t] - Ti[t]) + Ai / Ci * Ps[t] + 1.0/Ci * (Ph[t] + Pg[t])) # + si * dwi
    # dTe = (1.0/(Ce * Rie) * (Ti[t] - Te[t]) + 1.0/(Ce * Rea) * (Ta[t] - Te[t])) # + si * dwi
    
    # # Update temperatures
    # Ti[t+1] = Ti[t]+dTi
    # Te[t+1] = Te[t]+dTe

    # Thermostat control of heating power
    if Ti[t] < temp_setpoint - deadband:
        Ph[t+1] = Pheat_max
        error_int = 0
    elif Ti[t] > temp_setpoint + deadband:
        Ph[t+1] = 0.0
        error_int = 0
    else:
        error_prop = (temp_setpoint - Ti[t]) / temp_setpoint
        error_int += error_prop
        
        # dTi = (Ti[t] - Ti[t+1]) / Ti[t] # sweetspot: *100
        Ph_hat = Ph[t] 
        # Ph_hat += dTi * Ph_hat
        Ph_hat += (error_prop + error_int) * Ph_hat 
        
        Ph[t+1] = min(max(0, Ph_hat), Pheat_max)

    # Thermal RC-model of building 
    dTi = (1.0/(Ci * Rie) * (Te[t] - Ti[t]) + 1.0/(Ci * Ria) * (Ta[t] - Ti[t]) + Ai/Ci * Ps[t] + 1.0/Ci * (Ph[t] + Pg[t])) * timebase/3600 + np.random.normal()/np.sqrt(timesteps) # + si * dwi
    dTe = (1.0/(Ce * Rie) * (Ti[t] - Te[t]) + 1.0/(Ce * Rea) * (Ta[t] - Te[t])) * timebase/3600  + np.random.normal()/np.sqrt(timesteps) # + si * dwi
    
    # Update temperatures
    Ti[t+1] = Ti[t]+dTi
    Te[t+1] = Te[t]+dTe

    
    error.append(error_int)
    time.append(t)



timestamp = pd.date_range(start="2019-01-01", periods=len(Ti), freq="H")
sim_data_df = pd.DataFrame(index = pd.to_datetime(timestamp, format="%Y%m%d:%H%M"),
                           data = {"Ti": Ti,
                                   "Te": Te,
                                   "Ta": Ta,
                                   "Ps": Ps,
                                   "Ph": Ph,
                                   "Pg": Pg})

import matplotlib.dates as mdates
start = 210
end = int(start + 1*24 * 3600/timebase)

t_upper = np.ones(timesteps) * (temp_setpoint + deadband) - 273.15
t_lower = np.ones(timesteps) * (temp_setpoint - deadband) - 273.15

f, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(sim_data_df["Ti"][start:end]-273.15, label="Ti")
ax1.plot(sim_data_df["Ph"][start:end], label="Ph")
ax1.plot(sim_data_df["Ps"][start:end], label="Ps")
# # ax1.plot(time[start:end], t_upper[start:end], linestyle="dashed")
# ax1.plot(time[start:end], t_lower[start:end], linestyle="dashed")
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
ax1.legend()
ax1.grid()

ax2.plot(time[start:end], error[start:end], label="e")
ax2.legend()
ax2.grid()


# f, (ax1, ax2, ax3) = plt.subplots(3, 1)
# ax1.plot(time[start:end], sim_data_df["Ti"][start:end]-273.15, label="Ti")
# ax1.plot(time[start:end], sim_data_df["Te"][start:end]-273.15, label="Te")
# ax1.plot(time[start:end], sim_data_df["Ta"][start:end]-273.15, label="Ta")
# ax1.legend()
# ax1.grid()

# ax2.plot(time[start:end], sim_data_df["Ps"][start:end], label="Ps")
# ax2.plot(time[start:end], sim_data_df["Ph"][start:end], label="Ph")
# ax2.plot(time[start:end], sim_data_df["Pg"][start:end], label="Pg")
# ax2.legend()
# ax2.grid()

# ax3.plot(time[start:end], error[start:end])
# ax3.grid()
