import os
import random

import matplotlib.pyplot as plt
import pandas as pd
import psycopg
from dotenv import load_dotenv

# Load dataset
file_path = os.path.abspath(__file__)

csv_name = "Electricity_Profile.csv"
data_dir = os.path.join(os.path.dirname(file_path), "data", "alpg", csv_name)
df_profiles = pd.read_csv(data_dir, delimiter=";", header=None)
df_profiles.columns = pd.Index([f"{i}" for i in range(df_profiles.shape[1])])

timestamp = pd.date_range(start="2023-01-01", end="2024-01-01", freq="min")[:-1]
df_profiles.index = pd.Index(timestamp)

# Get average profile
df_profiles["mean_profile"] = df_profiles.mean(axis=1)

# Resample to 1h
df_profiles = df_profiles.resample("1h").mean()

# Make every profile the mean of the profile and the mean profile
for i in range(df_profiles.shape[1] - 1):
    df_profiles[str(i)] = (df_profiles[str(i)] + df_profiles["mean_profile"]) / 2

# Convert to kW
df_profiles = df_profiles / 1000

# Scale profiles to 1 kWh annual consumption
annual_consumption = df_profiles.sum(axis=0)
df_profiles = df_profiles.div(annual_consumption, axis=1)


def plot_profiles(df_profiles: pd.DataFrame) -> None:
    """Plot load profiles for two random days."""
    # Plot load profiles for two random days
    plt.figure(figsize=(30, 5))
    plt.title("Load Profiles")

    rand_int = random.randint(0, 360)

    for i in range(5):
        plt.plot(
            df_profiles[f"{i}"].iloc[24 * rand_int : 24 * (rand_int + 2)],
            label=f"Profile {i}",
        )

    plt.plot(
        df_profiles["mean_profile"].iloc[24 * rand_int : 24 * (rand_int + 2)],
        label="Mean Profile",
        color="black",
    )
    plt.xlabel("Time [h]")
    plt.ylabel("Power [kW]")
    plt.legend()
    plt.grid()
    plt.show()


def write_profiles_to_db(df_profiles: pd.DataFrame) -> None:
    """Write generated annual load profiles to PostgreSQL."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, "../../../.env")
    load_dotenv(env_path)
    database_url = os.environ["DATABASE_URL"]

    profiles_dict = df_profiles.to_dict(orient="list")
    rows = [
        (
            int(profile_id),
            "normalised annual loadprofile",
            [float(value) for value in profile],
        )
        for profile_id, profile in profiles_dict.items()
    ]

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO loadprofiles (profile_id, type, load_profile)
                VALUES (%s, %s, %s)
                ON CONFLICT (profile_id) DO UPDATE SET
                    type = EXCLUDED.type,
                    load_profile = EXCLUDED.load_profile
                """,
                rows,
            )
        conn.commit()

    print("Generated annual load profiles written to PostgreSQL database.")


plot_profiles(df_profiles)
write_profiles_to_db(df_profiles.drop(columns="mean_profile"))
