import time

from host.simHost import SimHost
from components.heating.heating import Heating


# Settings
# weather_data_file = "example_input_data.json"

start_time = time.time()

sim = SimHost()
sim.timebase = 60*60 # seconds

heating = Heating()
sim.add_component(heating)

heating.thermalModel.timebase = sim.timebase
sim.run_simulation()

end_time = time.time()
print(f"Execution time: {end_time - start_time} seconds.")





import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

connection = sim.db.engine.connect()
with sim.db.engine.connect() as conn:
    sim_data_df = pd.read_sql_table("ferntree_sim", con=conn)

timesteps = len(sim_data_df)
start = 210
end = int(start + 2*24 * 3600/sim.timebase)

t_upper = np.ones(timesteps) * (heating.temp_setpoint + heating.deadband) - 273.15
t_lower = np.ones(timesteps) * (heating.temp_setpoint - heating.deadband) - 273.15

f, (ax1) = plt.subplots(1, 1)
ax1.plot(sim_data_df["T_in"][start:end]-273.15, label="Ti")
ax1.plot(sim_data_df["P_heat_th"][start:end], label="Ph")
# ax1.plot(sim_data_df["Ps"][start:end], label="Ps")
# ax1.plot(np.linspace(start, end), t_upper[start:end], linestyle="dashed")
# ax1.plot(np.linspace(start, end), t_lower[start:end], linestyle="dashed")
# ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
ax1.legend()
ax1.grid()

# ax2.plot(time[start:end], heating.heatingCtrl.error[start:end], label="e")
# ax2.legend()
# ax2.grid()



# import pandas as pd
# import matplotlib.pyplot as plt

# connection = sim.db.engine.connect()
# with sim.db.engine.connect() as conn:
#     sim_data_df = pd.read_sql_table("ferntree_sim", con=conn)

# start = 200
# end = 224

# f, (ax1, ax2) = plt.subplots(2, 1)
# ax1.plot(sim_data_df["T_in"][start:end]-273.15, label="Ti")
# ax1.plot(sim_data_df["T_en"][start:end]-273.15, label="Te")
# ax1.plot(sim_data_df["T_amb"][start:end]-273.15, label="Ta")
# ax1.legend()
# ax1.grid()

# ax2.plot(sim_data_df["P_solar"][start:end], label="Ps")
# ax2.plot(sim_data_df["P_heat_th"][start:end], label="Ph")
# ax2.plot(sim_data_df["P_hgain"][start:end], label="Pg")
# ax2.legend()
# ax2.grid()

