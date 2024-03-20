import os
import pandas as pd

def create_season_day_models(data_dir, timebase):
    """ Process silver data to create gold data: 
    First, loadprofiles of all houses are sorted into seasons and weekday/weekend.
    Then, statistical models for the season-days are determined and saved to a csv file.
    The models will be used to generate synthetic load profiles in next step. They describe
    for each timestep of a season-day the mean, standard deviation, 5th, 25th, 75th and 95th percentile.
    Args:
        data_dir (str): Path to data directory
        timebase (int): Timebase of dataset in seconds   
    """
    print("\nSILVER: Create season-day models")
     # Load the preprocessed data
    silver_data = os.path.join(data_dir, "silver", "loadprofiles_silver.csv")
    print(f"Loading data from {silver_data}")
    df_raw = pd.read_csv(silver_data)
    df_raw["time"] = pd.to_datetime(df_raw["time"], unit="s")

    # Create pandas time series for one day with only the time
    timesteps_per_day = 24*60*60 // timebase
    time = pd.date_range(start="2023-01-01", periods=timesteps_per_day, freq=f"{timebase}s").time

    # Sort data into seasons (spring, summer, autumn, winter) and weekday/weekend
    df_spring_wd = pd.DataFrame(time, columns=["time"])
    df_spring_we = pd.DataFrame(time, columns=["time"])
    df_summer_wd = pd.DataFrame(time, columns=["time"])
    df_summer_we = pd.DataFrame(time, columns=["time"])
    df_autumn_wd = pd.DataFrame(time, columns=["time"])
    df_autumn_we = pd.DataFrame(time, columns=["time"])
    df_winter_wd = pd.DataFrame(time, columns=["time"])
    df_winter_we = pd.DataFrame(time, columns=["time"])

    print("Sorting data into seasons and weekday/weekend...")
    i = 0
    while i < len(df_raw):
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


    # Create dataframe with statistical models for each timestep of each season-day
    print("Determining statistical models for each season-day...")
    df_season_days = pd.DataFrame()
    season_days = [df_spring_wd, df_spring_we, df_summer_wd, df_summer_we, df_autumn_wd, df_autumn_we, df_winter_wd, df_winter_we]
    season_days_labels = ["spring_weekday", "spring_weekend", "summer_weekday", "summer_weekend", "autumn_weekday", "autumn_weekend", "winter_weekday", "winter_weekend"]
    for df, label in zip(season_days, season_days_labels):
        df.drop(columns=["time"], inplace=True)
        mean = df.mean(axis=1)
        std = df.std(axis=1)
        percentile95 = df.quantile(0.95, axis=1)
        percentile5 = df.quantile(0.05, axis=1)
        percentile75 = df.quantile(0.75, axis=1)
        percentile25 = df.quantile(0.25, axis=1)

        df_season_days[f"{label}_mean"] = mean
        df_season_days[f"{label}_std"] = std
        df_season_days[f"{label}_95th"] = percentile95
        df_season_days[f"{label}_5th"] = percentile5
        df_season_days[f"{label}_75th"] = percentile75
        df_season_days[f"{label}_25th"] = percentile25

    # Save df_season_day to csv
    season_days_path = os.path.join(data_dir, "gold", "season_days.csv")
    df_season_days.to_csv(season_days_path, index=False)
    print("Season days saved to gold/season_days.csv")
