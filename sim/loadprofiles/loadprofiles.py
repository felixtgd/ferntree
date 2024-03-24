import os
import pandas as pd
import matplotlib.pyplot as plt

import pipeline_bronze as bronze
import pipeline_silver as silver
import pipeline_gold as gold

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")
silver_dir = os.path.join(script_dir, "data", "silver")
gold_dir = os.path.join(script_dir, "data", "gold")

# BRONZE
# If necessary ingest bronze datasets to create silver dataset
if not os.path.isfile(os.path.join(silver_dir, "loadprofiles_sorted.csv")):
    bronze.ingest_datasets(data_dir, verbose=True)

# SILVER
# Timebase of dataset
timebase = 60*60 # 60 minutes
# Process silver dataset containing loadprofiles and determine statistical models for season-days
silver.create_season_day_models(data_dir, timebase)

# GOLD
# Generate annual load profiles for 100 houses
n_profiles = 10
gold.generate_annual_load_profiles(data_dir, n_profiles, timebase)


# VALIDATION
VALIDATION = False
if VALIDATION:
    # Load gold dataset
    gold_data = os.path.join(gold_dir, "annual_loadprofiles_gen.csv")
    df_profiles = pd.read_csv(gold_data)

    # Plot 5 random annual load profiles
    plt.figure(figsize=(30, 5))
    plt.title("Annual Load Profiles")

    timesteps_per_day = 24*60*60 // timebase
    timesteps_per_year = 365*timesteps_per_day
    time = pd.date_range(start="2023-01-01", periods=timesteps_per_year, freq=f"{timebase}s")

    day = 100*24
    for i in range(5):
        plt.plot(time[day:day+24*7], df_profiles[f"{i}"].iloc[day:day+24*7], label=f"Profile {i}")

    plt.xlabel("Time [h]")
    plt.ylabel("Power [W]")
    plt.legend()
    plt.grid()
    plt.show()