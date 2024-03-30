import json
import os
import sys
import importlib
import time

import numpy as np
import pandas as pd
import cvxpy as cp 
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
from sqlalchemy.orm import Session



# Path to model directory with model_congif.json and ferntree app
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.abspath(os.path.join(script_dir, '..', 'workspace/validation'))
ft_path = os.path.abspath(os.path.join(script_dir, '..', 'ferntree'))

# Load model-config.json
model_config_file = os.path.join(model_path, 'model_config.json')
with open(model_config_file, "r") as file:
    model_specs = json.load(file)

# Set up database connection
sys.path.insert(0, os.path.join(ft_path, "components"))
database = importlib.import_module('database.database')
orm_models= importlib.import_module('database.orm_models')
db = database.PostgresDatabase()
engine = create_engine(db.db_url)


# ----------SETUP AND RUN SIM----------
start_time = time.time()
# Model parameters
annual_consumption = 4000 # kWh
pv_size = 10 # kWp
bat_cap = 20 # kWh
bat_pwr = 5 # kW
bat_soc_init = 0 # kWh
print(f"baseload: {annual_consumption} kWh, PV: {pv_size} kWp, Battery: {bat_cap} kWh & {bat_pwr} kW")

# Write model specs to model_config.json
model_specs["house"]["baseload"]["annual_consumption"] = annual_consumption
model_specs["house"]["pv"]["peak_power"] = pv_size
model_specs["house"]["battery"]["capacity"] = bat_cap
model_specs["house"]["battery"]["max_power"] = bat_pwr

with open(model_config_file, 'w') as file:
    json.dump(model_specs, file, indent=4)

# Run simulation
os.system(f"python {ft_path}/ferntree.py -m validation")


# ----------SIM RESULTS----------
# Get results of simulation
with Session(engine) as session:
    results = session.query(orm_models.Timestep).all()

# Get power profiles
P_heat_el = np.array([row.P_heat_el for row in results]) # [kW], electrical heat demand
P_base = np.array([row.P_base for row in results]) # [kW], base load
P_pv = np.array([row.P_pv for row in results]) # [kW], pv production

# Net load profile of the house
P_net_load = P_heat_el + P_base + P_pv


# ----------QP OPTIMISATION----------
# GOAL: Find optimal battery profile that minimises 2-norm of total power profile of house
# Planning horizon
n = len(P_net_load)
# Decision variable x for QP optimisation --> power profile of battery
x = cp.Variable(n)

# Parameter: net load profile
p_net = cp.Parameter(n)
p_net.value = np.array(P_net_load)

# Elementwise constraint on x: max battery power
p_max = bat_pwr

# Lower bound on sum of x_i: -soc_init with safety margin of 10% of capacity
# Idea: Battery cannot discharge more than soc_init over total planning horizon
lb = -bat_soc_init + 0.1*bat_cap

# Upper bound on sum of x_i: c_bat-soc_init with safety margin of 10% of capacity
# Idea: Battery cannot charge more than delta between capacity and soc_init over total planning horizon
ub = bat_cap - bat_soc_init - 0.1 * bat_cap

# Objective: Minimize the 2-norm of the total power profile of the house
# PEAK SHAVING: We want a total power profile that is as flat as possible
objective = cp.Minimize(cp.norm(p_net + x, 2))

# Constraints
constraints = [x >= -p_max,
            x <= p_max,
            cp.cumsum(x) >= lb,
            cp.cumsum(x) <= ub]

# Solve quadratic optimisation problem
problem = cp.Problem(objective, constraints)
problem.solve(solver=cp.ECOS, ignore_dpp = True)

# Optimal power profile for battery
P_bat_qp = np.array(x.value)
# Resulting soc profile of battery
Soc_bat_qp = np.append(bat_soc_init, bat_soc_init+np.cumsum(P_bat_qp)[:-1]) # this only works when timebase is 1h


# ----------PROFILE PLOTS----------
# Plot power profiles for seven days
def plot_power_profiles(start=0, end=7*24):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Net load of house: P_heat + P_base + P_pv
    ax1.plot(time_series[start:end], P_net_load[start:end], color="tab:red", label='Net load [kW]')

    # Battery: QP Optimisation 
    ax1.plot(time_series[start:end], P_bat_qp[start:end], color="tab:blue", linestyle=':', label='Battery QP [kW]')
    ax1.plot(time_series[start:end], P_total_qp[start:end], color="tab:orange", linestyle=':', label='Total QP [kW]')

    # Battery: Valley filling approach
    ax1.plot(time_series[start:end], P_bat_valley[start:end], color="tab:green", label='Battery VF [kW]')
    ax1.plot(time_series[start:end], P_total_valley[start:end], color="tab:purple", label='Total VF [kW]')
    # Add straight lines at Z and -Z
    ax1.axhline(y=Z, color='r', linestyle='--')
    ax1.axhline(y=-Z, color='r', linestyle='--')

    ax2.plot(time_series[start:end], Soc_bat_qp[start:end], color="tab:blue", linestyle=':', label='QP')
    ax2.plot(time_series[start:end], Soc_bat_valley[start:end], color="tab:green", label='VF')
    # Plot straight lines for battery capacity and safety margins of 10%
    ax2.axhline(y=bat_cap, color='r', linestyle='--')
    ax2.axhline(y=0.9*bat_cap, color='r', linestyle=':')
    ax2.axhline(y=0.1*bat_cap, color='r', linestyle=':')

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Power [kW]')
    ax1.legend()
    ax1.grid()

    ax2.set_xlabel('Time')
    ax2.set_ylabel('SoC [kWh]')
    ax2.legend()
    ax2.grid()

    # Set title
    ax1.set_title(f'Z = {Z} kW, baseload: {annual_consumption} kWh, PV: {pv_size} kWp, Battery: {bat_cap} kWh & {bat_pwr} kW')

    # Save figure
    fig.savefig(os.path.join(script_dir, f'results/Z={Z}_power_profiles.png'))


# ----------VALLEY FILLING APPROACH----------
def set_battery_power(Z, p_t, soc_t, x_max, bat_cap):
    # GOAL: Find fill-level Z that corresponds to the optimal battery profile
    # if abs(p_t) < Z: x_t = 0 
    # if abs(p_t) - x_max > Z: x_t = -1 * sign(p_t) * x_max 
    # otherwise: x_t = -1 * sign(p_t) * (abs(p_t) - Z) 
    # --> shorthand: x_t = (-1) * sign(p_t) * max(0, min(abs(p_t) - Z, x_max))
    x_t = (-1) * np.sign(p_t) * max(0, min(abs(p_t) - Z, x_max))

    # Enforce feasibility of battery profile wrt. SoC
    x_t = min(x_t, 0.9*bat_cap - soc_t) # battery cannot charge more than capacity - soc_t
    x_t = max(x_t, -(soc_t-0.1*bat_cap)) # battery cannot discharge more than soc_t

    # Update state of charge
    soc_t += x_t

    return x_t, soc_t

# Try different values for Z
Z_list = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5] # fill-level [kW]

for Z in Z_list:
    P_bat_valley = np.zeros(n)
    Soc_bat_valley = np.zeros(n)
    soc_t = bat_soc_init
    # Simulate battery for one year with valley filling
    for t in range(n):
        Soc_bat_valley[t] = soc_t
        P_bat_valley[t], soc_t = set_battery_power(Z, P_net_load[t], soc_t, bat_pwr, bat_cap)

    # Total power profile of the house
    P_total_qp = P_net_load + P_bat_qp
    P_total_valley = P_net_load + P_bat_valley

    # Time series for one year
    time_series = np.array([row.time for row in results])
    # Convert time in seconds to datetime
    time_series = pd.to_datetime(time_series, unit='s')

    start = 1000
    end = start + 7*24
    # plot_power_profiles(start=start, end=end)



# ----------VALLEY FILLING WITH DYNAMIC Z----------
# 1. Optimise battery power profile 
def get_optimal_profile(P_load, bat_pwr, bat_cap, bat_soc):
    """
    QP optimisation with cvxpy
    Calculates the optimal battery profile that minimizes the 2-norm of the total power profile of a house.

    Args:
        P_load (list): The net load profile of the house.
        bat_pwr (float): The maximum power of the battery.
        bat_cap (float): The capacity of the battery.
        bat_soc (float): The current/initial state of charge (SoC) of the battery.

    Returns:
        numpy.ndarray: The optimal power profile for the battery.
    """
    # GOAL: Find optimal battery profile that minimises 2-norm of total power profile of house
    # Planning horizon: number of timesteps to consider in optimisation
    n = len(P_load)
    # Decision variable x for QP optimisation --> power profile of battery
    x = cp.Variable(n)

    # Parameter: net load profile
    p = cp.Parameter(n)
    p.value = np.array(P_load)

    # Elementwise constraint on x: max battery power
    x_max = bat_pwr

    # Lower bound on sum of x_i: -soc_init with safety margin of 10% of capacity
    # Idea: Battery cannot discharge more than soc_init over total planning horizon
    lb = -bat_soc + 0.1 * bat_cap

    # Upper bound on sum of x_i: c_bat-soc_init with safety margin of 10% of capacity
    # Idea: Battery cannot charge more than delta between capacity and soc_init over total planning horizon
    ub = bat_cap - bat_soc - 0.1 * bat_cap

    # Objective: Minimize the 2-norm of the total power profile of the house
    # PEAK SHAVING: We want a total power profile that is as flat as possible
    objective = cp.Minimize(cp.norm(p + x, 2))

    # Constraints
    constraints = [x >= -x_max,
                x <= x_max,
                cp.cumsum(x) >= lb,
                cp.cumsum(x) <= ub]

    # Solve quadratic optimisation problem
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.ECOS, ignore_dpp = True)

    # Optimal power profile for battery
    x_opt = np.array(x.value)
    return x_opt

# 2. Use optimal power profile to approximate Z_charge and Z_discharge
def set_fill_levels(P_total):
    """
    Calculate the fill levels Z_charge and Z_discharge for the battery 
    based on the optimal power profile.

    Args:
        P_total (numpy.ndarray): The total power profile of the house, 
        i.e. net load + optimal battery power --> P_total is the target
        profile we want to approximate using the Z values.

    Returns:
        tuple: The fill levels Z_charge and Z_discharge.
    """
    # Z_charge: used when net load is negative (i.e. generation) and battery gets charged
    if True:
        Z_charge = np.mean(P_total[P_total < 0]) if P_total[P_total < 0].size != 0 else -0.5
        Z_charge = 0.1 * Z_charge # reduce Z_charge to 10% of mean value
        # --> better to underestimate Z_charge than overestimate it:
        # if in doubt, better to make battery more "greedy" to increase self-consumption
    else:
        Z_charge = np.percentile(P_total[P_total < 0], 75) if P_total[P_total < 0].size != 0 else -0.5
    
    
    # Z_discharge: used when net load is positive (i.e. consumption) and battery gets discharged
    if True:
        Z_discharge = np.mean(P_total[P_total > 0]) if P_total[P_total > 0].size != 0 else 0.3
        Z_discharge = 0.1 * Z_discharge # reduce Z_discharge to 10% of mean value
    else:
        Z_discharge = np.percentile(P_total[P_total > 0], 0.1) if P_total[P_total > 0].size != 0 else 0.3
    
    return Z_charge, Z_discharge

# 3. Determine actual power profile using Z values
def set_battery_power(Z_charge, Z_discharge, p_t, soc_t, x_max, bat_cap):
    """ Use valley filling approach to determine battery power at current timestep
    - if abs(p_t) < Z: x_t = 0 
    - if abs(p_t) - x_max > Z: x_t = -1 * sign(p_t) * x_max 
    - otherwise: x_t = -1 * sign(p_t) * (abs(p_t) - Z) 
    
    Args:
        Z_charge (float): Fill level for charging the battery.
        Z_discharge (float): Fill level for discharging the battery.
        p_t (float): Net load of the house at current timestep.
        soc_t (float): Current state of charge of the battery.
        x_max (float): Maximum power of the battery.
        bat_cap (float): Capacity of the battery.

    Returns:
        tuple: The battery power x_t, updated state of charge soc_t, 
        and the applied fill level Z_t.
    """
    # Determine fill level Z_t based on net load
    if p_t >= 0: # net consumption --> battery discharges
        Z_t = Z_discharge
    else: # net generation --> battery charges
        Z_t = Z_charge

    # Determine battery power using valley filling approach
    x_t = (-1) * np.sign(p_t) * max(0, min(abs(p_t) - abs(Z_t), x_max))
    
    # Enforce feasibility of battery profile wrt. SoC
    # Additional constraints added with safety margins of 10% of capacity
    x_t = min(x_t, 0.9*bat_cap - soc_t) # battery cannot charge more than capacity - soc_t
    x_t = max(x_t, -(soc_t-0.1*bat_cap)) # battery cannot discharge more than soc_t

    # Update state of charge
    soc_t += x_t

    return x_t, soc_t, Z_t

# 4. Update prediction
def update_prediction(P_pred, p_t):
    """ Update prediction window for optimisation
    - Update prediction at current timestep with actual net load value
    - Shift prediction window by one timestep

    Args:
        P_pred (numpy.ndarray): Array with predicted power values.
        p_t (float): Net load of the house at current timestep.
    """
    update_factor = 0.2 # update factor/weight for current value in prediction window

    # Update: Take weighted average of current value and prediction
    p_updated = update_factor * p_t + (1 - update_factor) * P_pred[0]
    # Shift prediction window: Set first element to end of array
    P_pred[:-1] = P_pred[1:]
    P_pred[-1] = p_updated

    return P_pred


###### Simulate year

timebase = 60*60 # 1h
timesteps = int(365 * 24 * 3600 / timebase)
# Planning horizon of one day --> timesteps to consider 
planning_horizon = 24 * int(60 * 60 / timebase) # 24h
# Prediction window for optimisation
prediction_window = 1 * 24 * int(60 * 60 / timebase) # 7 days

# Initialise profiles
P_bat_valley = np.zeros(timesteps)
Soc_bat_valley = np.zeros(timesteps)
Z_cd = np.zeros(timesteps)
soc_t = bat_soc_init
P_predictions = np.zeros(timesteps)

# Predcition of P_net_load
P_load_pred = np.zeros(prediction_window)

# Simulate one year
for t in range(timesteps):
    # Get current net load
    p_t = P_net_load[t]
    # Update prediction of P_net_load
    P_load_pred = update_prediction(P_load_pred, p_t)

    # If t is start of new day, update Z values
    if t % planning_horizon == 0:
        # 1. Optimise battery power profile for prediction window
        # P_load_pred = P_net_load[t:t+prediction_window]
        # TODO: Find a way to guess Z values without optimisation
        # Optimisation is too time consuming, it should be possible to 
        # make a good guess for suitable Z values based on predictions 
        # P_bat_opt = get_optimal_profile(P_load_pred, bat_pwr, bat_cap, soc_t)

        # 2. Use optimal power profile to approximate Z_charge and Z_discharge
        # P_total = P_load_pred + P_bat_opt
        # Z_charge, Z_discharge = set_fill_levels(P_total)
        if False: # Option to choose greedy control strategy
            Z_charge, Z_discharge = (0.0, 0.0)
        else: 
            Z_charge, Z_discharge = set_fill_levels(P_load_pred)
        
    # 3. Determine battery power using Z values
    Soc_bat_valley[t] = soc_t
    P_bat_valley[t], soc_t, Z_t = set_battery_power(Z_charge, Z_discharge, p_t, soc_t, bat_pwr, bat_cap)
    Z_cd[t] = Z_t
    P_predictions[t] = P_load_pred[0]



def plot_power_profiles_vf(start=0, end=7*24):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Net load of house: P_heat + P_base + P_pv
    ax1.plot(time_series[start:end], P_net_load[start:end], color="tab:red", label='Net load [kW]')

    # Battery: QP Optimisation 
    ax1.plot(time_series[start:end], P_bat_qp[start:end], color="tab:blue", linestyle=':', label='Battery QP [kW]')
    ax1.plot(time_series[start:end], P_total_qp[start:end], color="tab:orange", linestyle=':', label='Total QP [kW]')

    # Battery: Valley filling approach
    ax1.plot(time_series[start:end], P_bat_valley[start:end], color="tab:green", label='Battery VF [kW]')
    ax1.plot(time_series[start:end], P_total_valley[start:end], color="tab:purple", label='Total VF [kW]')
    # Add straight lines at Z_charge and Z_discharge
    ax1.plot(time_series[start:end], Z_cd[start:end], color="tab:grey", label='Z_cd [kW]')
    ax1.plot(time_series[start:end], P_predictions[start:end], color="tab:pink", label='P_pred [kW]')

    # Add text box with 2-norm of total power profile
    ax1.text(0.05, 0.95, f"2-norm QP: {np.linalg.norm(P_total_qp):.2f} \
             \n2-norm VF: {np.linalg.norm(P_total_valley):.2f}", transform=ax1.transAxes, fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

    ax2.plot(time_series[start:end], Soc_bat_qp[start:end], color="tab:blue", linestyle=':', label='QP')
    ax2.plot(time_series[start:end], Soc_bat_valley[start:end], color="tab:green", label='VF')
    # Plot straight lines for battery capacity and safety margins of 10%
    ax2.axhline(y=bat_cap, color='r', linestyle='--')
    ax2.axhline(y=0.9*bat_cap, color='r', linestyle=':')
    ax2.axhline(y=0.1*bat_cap, color='r', linestyle=':')

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Power [kW]')
    ax1.legend()
    ax1.grid()

    ax2.set_xlabel('Time')
    ax2.set_ylabel('SoC [kWh]')
    ax2.set_ylim(bottom=0)
    ax2.legend()
    ax2.grid()

    # Set title
    ax1.set_title(f'Z_charge mean = {np.mean(Z_charge):.2f} kW, Z_discharge = {np.mean(Z_discharge):.2f} kW, baseload: {annual_consumption} kWh, PV: {pv_size} kWp, Battery: {bat_cap} kWh & {bat_pwr} kW')

    # Save figure
    fig.savefig(os.path.join(script_dir, f'results/Z={np.mean(Z_charge):.2f}_{np.mean(Z_discharge):.2f}_power_profiles.png'))

# Total power profile of the house
P_total_qp = P_net_load + P_bat_qp
P_total_valley = P_net_load + P_bat_valley

# Time series for one year
time_series = np.array([row.time for row in results])
# Convert time in seconds to datetime
time_series = pd.to_datetime(time_series, unit='s')

start = 2000
end = start + 7*24
plot_power_profiles_vf(start=start, end=end)


end_time = time.time()
print(f"Execution time: {(end_time - start_time):.2f} seconds.")