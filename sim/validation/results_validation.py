
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import orm_models
from database import database

import matplotlib.pyplot as plt
from datetime import datetime

# Connect to database and get results from table "ferntree_sim"
db = database.PostgresDatabase()
engine = create_engine(db.db_url)
with Session(engine) as session:
    results = session.query(orm_models.Timestep).all()

# Create array with datatime timestamps from time column in results
timestamps = [datetime.fromtimestamp(row.time) for row in results]

# Create a figure with two subplots:
# One for ambient and indoor temperature for a week
# One for solar irradiance and heating power for a week
def plot_results(timestamps, results):
    fig, axs = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle('Simulation results for a week')
    axs[0].plot(timestamps, [row.T_amb - 273.15 for row in results], label='Ambient temperature')
    axs[0].plot(timestamps, [row.T_in  - 273.15 for row in results], label='Indoor temperature')
    axs[0].plot(timestamps, [row.T_en  - 273.15 for row in results], label='Envelope temperature')
    axs[0].set_ylabel('Temperature [°C]')
    axs[0].legend()
    axs[0].grid()

    axs[1].plot(timestamps, [row.P_solar for row in results], label='Solar irradiance')
    axs[1].plot(timestamps, [row.P_heat_th for row in results], label='Thermal heating power')
    axs[1].plot(timestamps, [row.P_heat_el for row in results], label='Electr heating power')
    axs[1].plot(timestamps, [row.P_hgain for row in results], label='Internal heat gain')
    axs[1].set_ylabel('Power [kW]')
    axs[1].legend()
    axs[1].grid()

    plt.show()

# Plot results for a ween in february
week = 5
start_idx = 24*7*week
# end_idx = 24*7*(week+1)
end_idx = start_idx + 24*3
# plot_results(timestamps[start_idx:end_idx], results[start_idx:end_idx])


# Plot the load duration curve of the thermal heating power
def plot_load_duration_curve(results):
    P_heat_th = [row.P_heat_th for row in results]
    P_heat_th.sort(reverse=True)
    plt.plot(P_heat_th)
    plt.title('Load duration curve of the thermal heating power')
    plt.xlabel('Timestep')
    plt.ylabel('Power [kW]')
    plt.grid()
    plt.show()

# plot_load_duration_curve(results)
    
# Plot the cumulative energy demand for heating
def plot_cumulative_energy_demand(results):
    P_heat_th = [row.P_heat_th for row in results]
    energy_demand = [sum(P_heat_th[:i]) for i in range(len(P_heat_th))]
    plt.plot(energy_demand)
    plt.title('Cumulative energy demand for heating')
    plt.xlabel('Timestep')
    plt.ylabel('Energy [kWh]')
    plt.grid()
    plt.show()

plot_cumulative_energy_demand(results)