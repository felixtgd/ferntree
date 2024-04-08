import json
import os
import sys
import importlib
import time

import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
from sqlalchemy.orm import Session


# Path to model directory with model_congif.json and ferntree app
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.abspath(os.path.join(script_dir, "..", "workspace/validation"))
ft_path = os.path.abspath(os.path.join(script_dir, "..", "ferntree"))

# Load model-config.json
model_config_file = os.path.join(model_path, "model_config.json")
with open(model_config_file, "r") as file:
    model_specs = json.load(file)

# Set up database connection
sys.path.insert(0, os.path.join(ft_path, "components"))
database = importlib.import_module("database.database")
orm_models = importlib.import_module("database.orm_models")
db = database.PostgresDatabase()
engine = create_engine(db.db_url)


# ----------SETUP AND RUN SIM----------
start_time = time.time()
# Model parameters
annual_consumption = 2339  # kWh
pv_size = 10  # kWp
bat_cap = 20  # kWh
bat_pwr = 5  # kW
bat_soc_init = 0  # kWh
print(
    f"baseload: {annual_consumption} kWh, PV: {pv_size} kWp, Battery: {bat_cap} kWh & {bat_pwr} kW"
)

# Write model specs to model_config.json
model_specs["house"]["baseload"]["annual_consumption"] = annual_consumption
model_specs["house"]["pv"]["peak_power"] = pv_size
model_specs["house"]["battery"]["capacity"] = bat_cap
model_specs["house"]["battery"]["max_power"] = bat_pwr

with open(model_config_file, "w") as file:
    json.dump(model_specs, file, indent=4)

# Run simulation
os.system(f"python {ft_path}/ferntree.py -m validation")


# ----------SIM RESULTS----------
# Get results of simulation
with Session(engine) as session:
    results = session.query(orm_models.Timestep).all()

measurements = {
    "time": [],
    "T_amb": [],
    "P_solar": [],
    "T_in": [],
    "T_en": [],
    "P_heat_th": [],
    "P_heat_el": [],
    "P_base": [],
    "P_pv": [],
    "P_bat": [],
    "Soc_bat": [],
    "fill_level": [],
    "P_load_pred": [],
}

for result in results:
    measurements["time"].append(result.time)
    measurements["T_amb"].append(result.T_amb)
    measurements["P_solar"].append(result.P_solar)
    measurements["T_in"].append(result.T_in)
    measurements["T_en"].append(result.T_en)
    measurements["P_heat_th"].append(result.P_heat_th)
    measurements["P_heat_el"].append(result.P_heat_el)
    measurements["P_base"].append(result.P_base)
    measurements["P_pv"].append(result.P_pv)
    measurements["P_bat"].append(result.P_bat)
    measurements["Soc_bat"].append(result.Soc_bat)
    measurements["fill_level"].append(result.fill_level)
    measurements["P_load_pred"].append(result.P_load_pred)

# Convert to pandas dataframe
df = pd.DataFrame(measurements)
df["time"] = pd.to_datetime(df["time"], unit="s")
df.set_index("time", inplace=True)

df["P_net_load"] = df["P_base"] + df["P_pv"] + df["P_heat_el"]
df["P_total"] = df["P_net_load"] + df["P_bat"]


# ----------PLOT RESULTS----------
def plot_results(df_annual, month):
    start = int(8760 / 12 * month) + 7 * 24
    end = start + 7 * 24
    df = df_annual.iloc[start:end]

    annual_baseload_demand = df_annual["P_base"].sum() / 1000
    annual_heating_demand_th = df_annual["P_heat_th"].sum() / 1000
    annual_heating_demand_el = df_annual["P_heat_el"].sum() / 1000
    annual_pv_generation = df_annual["P_pv"].sum() / 1000
    annual_grid_consumption = (
        df_annual["P_total"][df_annual["P_total"] > 0.0].sum() / 1000
    )
    annual_grid_feed_in = df_annual["P_total"][df_annual["P_total"] < 0.0].sum() / 1000

    diff_soc = (df_annual["Soc_bat"].iloc[-1] - bat_soc_init) / 1000
    annual_self_consumption = (
        annual_baseload_demand + annual_heating_demand_el - annual_grid_consumption
    )

    fig, axs = plt.subplots(3, 1, figsize=(20, 15))

    # Plot 1: T_amp, T_in, T_en, P_solar, P_heat_th
    axs[0].plot(df.index, df["T_amb"] - 273.15, label="T_amb")
    axs[0].plot(df.index, df["T_in"] - 273.15, label="T_in")
    axs[0].plot(df.index, df["T_en"] - 273.15, label="T_en")
    axs[0].plot(df.index, df["P_solar"], label="P_solar")
    axs[0].plot(df.index, df["P_heat_th"], label="P_heat_th")
    axs[0].set_ylabel("Temperature [°C] / Power [kW]")
    axs[0].legend()
    axs[0].grid()
    # Add textbox with annual thermal energy demand
    textstr = f"Thermal energy demand: {annual_heating_demand_th:.3f} MWh/a"
    props = dict(boxstyle="round", facecolor="white", alpha=0.5)
    axs[0].text(
        0.05,
        0.95,
        textstr,
        transform=axs[0].transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
    )

    # Plot 2: P_base, P_pv, P_heat_el, P_bat, P_total, P_net_load, P_load_pred, fill_level
    axs[1].plot(df.index, df["P_base"], label="P_base")
    axs[1].plot(df.index, df["P_pv"], label="P_pv")
    axs[1].plot(df.index, df["P_heat_el"], label="P_heat_el")
    axs[1].plot(df.index, df["P_bat"], label="P_bat")
    axs[1].plot(df.index, df["P_total"], label="P_total")
    axs[1].plot(df.index, df["P_net_load"], color="tab:grey", label="P_net_load")
    axs[1].plot(
        df.index,
        df["P_load_pred"],
        color="tab:grey",
        linestyle=":",
        label="P_load_pred",
    )
    axs[1].plot(df.index, df["fill_level"], color="black", label="fill_level")
    axs[1].set_ylabel("Power [kW]")
    axs[1].legend()
    axs[1].grid()

    # Plot 3: Soc_bat
    axs[2].plot(df.index, df["Soc_bat"], label="Soc_bat")
    axs[2].axhline(bat_cap, color="black", linestyle="--")
    axs[2].axhline(0.1 * bat_cap, color="black", linestyle=":")
    axs[2].axhline(0.9 * bat_cap, color="black", linestyle=":")
    axs[2].set_ylabel("State of charge [kWh]")
    axs[2].set_ylim(bottom=0)
    axs[2].legend()
    axs[2].grid()
    # Add textbox with annual baseload demand, heating demand, pv generation, consumption from grid, grid feed-in, self-consumption
    textstr = (
        f"Baseload demand: {annual_baseload_demand:.3f} MWh/a\n"
        f"Heating demand (el): {annual_heating_demand_el:.3f} MWh/a\n"
        f"PV generation: {annual_pv_generation:.3f} MWh/a\n"
        f"Consumption from grid: {annual_grid_consumption:.3f} MWh/a\n"
        f"Grid feed-in: {annual_grid_feed_in:.3f} MWh/a\n"
        f"Self-consumption: {annual_self_consumption:.3f} MWh/a ({annual_self_consumption/(annual_baseload_demand+annual_heating_demand_el) * 100:.3f}%)\n"
        f"Diff. Bat. SoC: {diff_soc:.3f} MWh"
    )
    props = dict(boxstyle="round", facecolor="white", alpha=0.5)
    axs[2].text(
        0.05,
        0.95,
        textstr,
        transform=axs[2].transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
    )

    # Set title of figure with annual consumption, pv size, battery capacity and power
    axs[0].set_title(
        f"Annual consumption: {annual_consumption} kWh, PV: {pv_size} kWp, Battery: {bat_cap} kWh & {bat_pwr} kW"
    )

    # Save figure
    fig.savefig(os.path.join(script_dir, f"{month}_sim_results_complete.png"))


months = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
for month in months:
    plot_results(df, month)


end_time = time.time()
print(f"Execution time: {(end_time - start_time):.2f} seconds.")
