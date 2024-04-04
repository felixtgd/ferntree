import os
import numpy as np
import pandas as pd

from sqlalchemy import URL, create_engine

# Generate yearly load profiles
# - Create 100 profiles & get mean annual consumption of all (will be default value if user does not specify)
# - Normalise all profiles to 1kWh annual consumption
# - In sim, each user gets one random number between 0 and 100 that determines load profile,
# then profile is set and scaled to specified (or default) annual consumption
# --> This should safe time, since there is no need to always generate a new profile for each user, couple of
# "standard" profiles should be enough


def generate_annual_load_profiles(data_dir, n_profiles, timebase):
    """Generate annual load profiles for n houses. For each day of the year,
    a load profile is generated based on the season-day model. The daily profiles
    are concatenated to an annual profile.
    Args:
        data_dir (str): Path to data directory
        n_profiles (int): Number of annual profiles to generate
        timebase (int): Timebase of profiles in seconds
    """
    print("\nGOLD: Generate annual load profiles")
    # Load models of season-days
    season_days_path = os.path.join(data_dir, "gold", "season_days_models.csv")
    df_season_days = pd.read_csv(season_days_path)

    # Create dataframe for annual load profiles
    df_profiles = pd.DataFrame()

    # Create time series for one year
    timesteps_per_day = 24 * 60 * 60 // timebase
    timesteps_per_year = 365 * timesteps_per_day
    time = pd.date_range(
        start="2023-01-01", periods=timesteps_per_year, freq=f"{timebase}s"
    )

    print(f"Generating annual load profiles for {n_profiles} houses...")
    for n in range(n_profiles):
        annual_profile = []

        if n % 10 == 0:
            print(f"Generating profile #{n}...")

        i = 0
        # Generate daily profiles for respective season-days and concatenate to annual profile
        while i < len(time):  # - timesteps_per_day:
            # Get weekday and month of current row
            month = time[i].month
            weekday = time[i].weekday()

            # Spring
            if month in [3, 4, 5]:
                if weekday < 5:  # Weekday
                    season_day = "spring_weekday"
                else:  # Weekend
                    season_day = "spring_weekend"

            # Summer
            elif month in [6, 7, 8]:
                if weekday < 5:  # Weekday
                    season_day = "summer_weekday"
                else:  # Weekend
                    season_day = "summer_weekend"

            # Autumn
            elif month in [9, 10, 11]:
                if weekday < 5:  # Weekday
                    season_day = "autumn_weekday"
                else:  # Weekend
                    season_day = "autumn_weekend"

            # Winter
            else:
                if weekday < 5:  # Weekday
                    season_day = "winter_weekday"
                else:  # Weekend
                    season_day = "winter_weekend"

            # Generate daily profile with the current season-day model
            mean = df_season_days[f"{season_day}_mean"]
            std = df_season_days[f"{season_day}_std"]
            p5 = df_season_days[f"{season_day}_5th"]
            p95 = df_season_days[f"{season_day}_95th"]
            # p25 = df_season_days[f"{season_day}_25th"]
            # p75 = df_season_days[f"{season_day}_75th"]

            daily_profile = generate_daily_profile(mean, std, p5, p95)
            # Concatenate daily profiles to annual profile
            annual_profile.extend(daily_profile)

            # Increase i by one day
            i += timesteps_per_day

        # Add annual profile to dataframe
        df_profiles[f"{n}"] = annual_profile

    # Set power values to kW
    df_profiles = df_profiles / 1e3
    # Calculate annual consumption for each profile
    annual_consumption = df_profiles.sum(axis=0) * timebase / (60 * 60)
    # Scale annual profiles to 1kWh annual consumption
    df_profiles = df_profiles.div(annual_consumption, axis=1)

    print("Annual consumption:")
    print(f"Mean: {annual_consumption.mean():.2f} kWh")
    print(f"Max: {annual_consumption.max():.2f} kWh")
    print(f"Min: {annual_consumption.min():.2f} kWh")
    print(f"Scaled to 1kWh: {df_profiles.sum(axis=0).mean():.2f}")

    # Save annual consumption to csv
    output_file = os.path.join(data_dir, "gold", "annual_consumption_gen.csv")
    annual_consumption.to_csv(output_file, index=False)
    print("Annual consumption saved to gold/annual_consumption_gen.csv")

    # Save generated annual profiles to csv
    output_file = os.path.join(data_dir, "gold", "annual_loadprofiles_gen.csv")
    df_profiles.to_csv(output_file, index=False)
    print("Generated annual load profiles saved to gold/annual_loadprofiles_gen.csv")
    print(f"Timesteps: {len(df_profiles)}, Num. profiles: {len(df_profiles.columns)}")

    # Write generated annual load profiles to database
    write_profiles_to_db(df_profiles)


def generate_daily_profile(mean, std, lb, ub):
    """Generate daily load profile for each season-day
    Args:
        mean (float): Array of means for n timesteps
        std (float): Array of standard deviations for n timesteps
        lb (float): Array of lower bound values (e.g. 25th perc.) for n timesteps
        ub (float): Array of upper bound values (e.g. 75th perc.) for n timesteps
    Returns:
        profile (float): Load profile with n-timesteps
    """
    # Reduce standard deviation to make profiles smoother
    std = std / 2.0
    # Generate profile with normal distribution
    profile = np.random.normal(mean, std)
    # Truncate profile to min and max values
    lb = np.maximum(lb, 0)
    profile = np.maximum(np.minimum(profile, ub), lb)

    return profile


def write_profiles_to_db(df_profiles):
    # Write generated annual load profiles to database
    host = "localhost"
    port = "5432"
    db_name = "sim_db"
    db_url = URL.create(
        "postgresql+psycopg2",
        host=host,
        port=port,
        database=db_name,
    )

    engine = create_engine(db_url)

    # Export to database
    df_profiles.to_sql(
        "annual_loadprofiles", con=engine, if_exists="replace", index=False
    )
    print(f"Exported generated annual load profiles to database at {db_url}")
