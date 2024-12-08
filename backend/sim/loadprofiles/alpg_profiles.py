import os
import random
from typing import Hashable, Union

import certifi
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import InsertManyResult
from pymongo.server_api import ServerApi

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
    """Write generated annual load profiles to MongoDB database."""
    # Write generated annual load profiles to MongoDB database
    # Use certifi to get the path of the CA file
    ca: str = certifi.where()

    # Load config from .env file:
    scipt_dir: str = os.path.dirname(os.path.abspath(__file__))
    env_path: str = os.path.join(scipt_dir, "../../.env")
    load_dotenv(env_path)
    MONGODB_URI: str = os.environ["MONGODB_URI"]

    client: MongoClient = MongoClient(
        MONGODB_URI, server_api=ServerApi("1"), tlsCAFile=ca
    )
    db: Database = client["ferntree_db"]
    collection: Collection = db["loadprofiles"]

    # Convert dataframe to dictionary
    profiles_dict: dict[Hashable, list[float]] = df_profiles.to_dict(orient="list")

    # Write each profile as a separate document to database
    profile_docs: list[dict[str, Union[str, int, list[float]]]] = [
        {
            "type": "normalised annual loadprofile",
            "profile_id": int(str(profile_id)),
            "load_profile": profile,
        }
        for profile_id, profile in profiles_dict.items()
    ]
    doc_ids: InsertManyResult = collection.insert_many(profile_docs)
    # Create an index on the 'profile_id' field
    collection.create_index("profile_id")

    if doc_ids:
        print("Generated annual load profiles written to MongoDB database.")
    else:
        print("Error writing annual load profiles to MongoDB database.")

    client.close()


plot_profiles(df_profiles)
write_profiles_to_db(df_profiles.drop(columns="mean_profile"))
