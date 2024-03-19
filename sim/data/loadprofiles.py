import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from preprocessing import preprocess_loadprofiles

# dataset_raw = "data_loadprofiles/loadprofiles_raw_15min.csv"
dataset_raw = "data_loadprofiles/loadprofiles_raw.csv"

# Timebase of dataset
timebase = 60*60 # 60 minutes
timesteps_per_day = 24*60*60 // timebase

# Check if loadprofiles.csv exists
if not os.path.isfile(dataset_raw):
    preprocess_loadprofiles()

# Load the preprocessed data
df_raw = pd.read_csv(dataset_raw)
df_raw["time"] = pd.to_datetime(df_raw["time"], unit="s")

# Create pandas time series for one day with only the time
time = pd.date_range(start="2023-01-01", periods=timesteps_per_day, freq=f"{timebase}s").time

# Sort data into seasons (spring, summer, autumn, winter) and weekday/weekend
cols = df_raw.columns
df_spring_wd = pd.DataFrame(time, columns=["time"])
df_spring_we = pd.DataFrame(time, columns=["time"])
df_summer_wd = pd.DataFrame(time, columns=["time"])
df_summer_we = pd.DataFrame(time, columns=["time"])
df_autumn_wd = pd.DataFrame(time, columns=["time"])
df_autumn_we = pd.DataFrame(time, columns=["time"])
df_winter_wd = pd.DataFrame(time, columns=["time"])
df_winter_we = pd.DataFrame(time, columns=["time"])

i = 0
while i < len(df_raw) - timesteps_per_day:
    # Get weekday and month of current row
    month = df_raw["time"].iloc[i].month
    weekday = df_raw["time"].iloc[i].weekday()

    # print(f"{i}: Month: {month}, Weekday: {weekday}")

    batch = df_raw.iloc[i:i+timesteps_per_day].copy()
    batch["time"] = batch["time"].dt.time
    # Rename columns to avoid duplicate column names
    batch.columns = [f"{col}_{i}" if col != "time" else col for col in batch.columns]

    # Sort daily battches of rows into seasons and weekday/weekend
    # Merge rows with respective dataframe

    # Spring
    if month in [3, 4, 5]: 
        if weekday < 5: # Weekday
            df_spring_wd = pd.merge(df_spring_wd, batch, on="time", how="outer")
        else: # Weekend
            df_spring_we = pd.merge(df_spring_we, batch, on="time", how="outer")
    
    # Summer
    elif month in [6, 7, 8]:
        if weekday < 5: # Weekday
            df_summer_wd = pd.merge(df_summer_wd, batch, on="time", how="outer")
        else: # Weekend
            df_summer_we = pd.merge(df_summer_we, batch, on="time", how="outer")
    
    # Autumn
    elif month in [9, 10, 11]:
        if weekday < 5: # Weekday
            df_autumn_wd = pd.merge(df_autumn_wd, batch, on="time", how="outer")
        else: # Weekend
            df_autumn_we = pd.merge(df_autumn_we, batch, on="time", how="outer")
    
    # Winter
    else:
        if weekday < 5: # Weekday
            df_winter_wd = pd.merge(df_winter_wd, batch, on="time", how="outer")
        else: # Weekend
            df_winter_we = pd.merge(df_winter_we, batch, on="time", how="outer")
    
    i += timesteps_per_day


# Create dataframe with mean and standard deviation for each timestep of each season-day
df_season_day = pd.DataFrame()
season_days = [df_spring_wd, df_spring_we, df_summer_wd, df_summer_we, df_autumn_wd, df_autumn_we, df_winter_wd, df_winter_we]
season_days_labels = ["spring_weekday", "spring_weekend", "summer_weekday", "summer_weekend", "autumn_weekday", "autumn_weekend", "winter_weekday", "winter_weekend"]
for df, label in zip(season_days, season_days_labels):
    df.drop(columns=["time"], inplace=True)
    mean = df.mean(axis=1)
    std = df.std(axis=1)
    # max = df.max(axis=1)
    # min = df.min(axis=1)
    percentile95 = df.quantile(0.95, axis=1)
    percentile5 = df.quantile(0.05, axis=1)
    percentile75 = df.quantile(0.75, axis=1)
    percentile25 = df.quantile(0.25, axis=1)

    df_season_day[f"{label}_mean"] = mean
    df_season_day[f"{label}_std"] = std
    df_season_day[f"{label}_95th"] = percentile95
    df_season_day[f"{label}_5th"] = percentile5
    df_season_day[f"{label}_75th"] = percentile75
    df_season_day[f"{label}_25th"] = percentile25



def generate_daily_profile(mean, std, min, max):
    """ Generate daily load profile for each season-day
    Args:
        mean (float): Array of means for n timesteps
        std (float): Array of standard deviations for n timesteps
        min (float): Array of min values (e.g. 25th perc.) for n timesteps
        max (float): Array of max values (e.g. 75th perc.) for n timesteps
    Returns:
        profile (float): Load profile with n-timesteps
    """
    # Reduce standard deviation to make profiles smoother
    std = std/10.0
    # Generate profile with normal distribution
    profile = np.random.normal(mean, std)
    # Truncate profile to min and max values
    min = np.maximum(min, 0)
    profile = np.maximum(np.minimum(profile, max), min)

    return profile

# Generate daily load profile for each season-day
df_profiles = pd.DataFrame()
for label in season_days_labels:
    mean = df_season_day[f"{label}_mean"]
    std = df_season_day[f"{label}_std"]
    p5 = df_season_day[f"{label}_5th"]
    p95 = df_season_day[f"{label}_95th"]
    p25 = df_season_day[f"{label}_25th"]
    p75 = df_season_day[f"{label}_75th"]

    profile = generate_daily_profile(mean, std, p25, p75)
    df_profiles[label] = profile

# Plot daily load profiles
fig, ax = plt.subplots(figsize=(12, 8))
for label in ["spring_weekday", "summer_weekday", "autumn_weekday", "winter_weekday"]:
    ax.plot(df_profiles[label], label=label)

ax.set_title("Daily load profiles")
ax.grid()
ax.legend()
plt.show()

# Generate yearly load profile
# Create 100 profiles, get mean annual consumption of all (will be default value if user does not specify),
# normalise all profiles to 1kWh annual consumption, in sim each user gets one random number between 0 and 100
# that determines load profile, then profile is set and scaled to specified (or default) annual consumption
# this should safe time, since there is no need to always generate a new profile for each user, couple of 
# "standard" profiles should be enough


def plot_season_day(df, season, day):
    df = df.copy()

    fig, ax = plt.subplots(figsize=(12, 8))

    time = pd.to_datetime(df["time"], format="%H:%M:%S").dt.time
    time = [t.hour * 3600 + t.minute * 60 + t.second for t in time]
    df.set_index("time", inplace=True)

    mean = df.mean(axis=1)
    max = df.max(axis=1)
    min = df.min(axis=1)
    percentile95 = df.quantile(0.95, axis=1)
    percentile5 = df.quantile(0.05, axis=1)
    percentile75 = df.quantile(0.75, axis=1)
    percentile25 = df.quantile(0.25, axis=1)

    percentile60 = df.quantile(0.6, axis=1)
    percentile40 = df.quantile(0.4, axis=1)

    ax.plot(time, mean, color="tab:blue", label="Mean")
    # ax.plot(time, max, color="black", label="Max")
    # ax.plot(time, min, color="black", label="Min")
    ax.plot(time, percentile95, color="tab:red", linestyle="-", label="95th percentile")
    ax.plot(time, percentile5, color="tab:red", linestyle=":", label="5th percentile")
    ax.plot(time, percentile75, color="tab:orange", linestyle="-", label="75th percentile")
    ax.plot(time, percentile25, color="tab:orange", linestyle=":", label="25th percentile")
    # ax.plot(time, percentile60, color="tab:orange", label="60th percentile")
    # ax.plot(time, percentile40, color="tab:orange", label="40th percentile")

    # Select two random houses
    cols = df.columns
    idx = np.random.randint(0, len(cols))
    house1 = cols[idx]
    idx = np.random.randint(0, len(cols))
    house2 = cols[idx]
    # ax.plot(time, df[house1], color="tab:purple", linestyle="-.", label=house1)
    # ax.plot(time, df[house2], color="tab:green", linestyle="-.", label=house2)

    

    ax.set_title(f"Loadprofiles {season} {day}")
    ax.grid()
    ax.legend()

    plt.show()

    # Save figure
    fig.savefig(f"loadprofiles_{season}_{day}.png")


# plot_season_day(df_spring_wd, "spring", "weekday")
# plot_season_day(df_summer_wd, "summer", "weekday")
# plot_season_day(df_autumn_wd, "autumn", "weekday")
# plot_season_day(df_winter_wd, "winter", "weekday")


