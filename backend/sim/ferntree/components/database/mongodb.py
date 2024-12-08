import os
from datetime import datetime
from typing import Any, Optional

import certifi
from bson.objectid import ObjectId
from components.database.models import LoadProfile, TimestepData
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.server_api import ServerApi

# Use certifi to get the path of the CA file
ca: str = certifi.where()

# Load config from .env file:
scipt_dir: str = os.path.dirname(os.path.abspath(__file__))
env_path: str = os.path.join(scipt_dir, "../../../../.env")
load_dotenv(env_path)
MONGODB_URI: str = os.environ["MONGODB_URI"]
MONGODB_DATABASE: str = os.environ["MONGODB_DATABASE"]


class pyMongoClient:
    """Class for interacting with the MongoDB database."""

    def __init__(self, sim_id: str, model_id: str) -> None:
        """Initializes a new instance of the pyMongoClient class.

        Args:
            sim_id (str): id of simulation doc in db
            model_id (str): id of model doc in db

        """
        self.client: MongoClient = MongoClient(
            MONGODB_URI, server_api=ServerApi("1"), tlsCAFile=ca
        )

        self.db: Database = self.client[MONGODB_DATABASE]
        self.results_collection: Collection = self.db["sim_results_ts"]
        self.results_collection.create_index("sim_id", unique=True)
        self.results_collection.create_index("model_id", unique=True)

        # Replace the document if it exists, or insert a new one
        self.results_collection.replace_one(
            {"sim_id": sim_id},
            {
                "sim_id": sim_id,
                "model_id": model_id,
                "run_time": datetime.now().isoformat(),
            },
            upsert=True,
        )

        self.sim_id: str = sim_id

        self.batch_size: int = 1000
        self.data_buffer: list[Any] = []

    def load_config(self) -> dict[str, Any]:
        """Load simulation configuration from the database.

        Returns:
            dict: Simulation configuration

        """
        collection = self.db["simulations"]
        result: Optional[dict[str, Any]] = collection.find_one(
            {"_id": ObjectId(self.sim_id)}
        )  # noqa: E501

        if result is None:
            raise ValueError(f"Simulation with id {self.sim_id} not found in database.")

        return result

    def get_load_profile(self, profile_id: int) -> list[float]:
        """Get load profile for baseload from database.

        Args:
            profile_id (int): id of load profile in db

        Returns:
            list: Load profile

        """
        collection = self.db["loadprofiles"]
        doc: Optional[dict[str, Any]] = collection.find_one({"profile_id": profile_id})

        if doc is None:
            raise ValueError(
                f"Load profile with id {profile_id} not found in database."
            )  # noqa: E501

        lp_data: LoadProfile = LoadProfile(**doc)
        load_profile: list[float] = lp_data.load_profile

        return load_profile

    def write_timeseries_data_to_db(self, results: dict[str, Any]) -> None:
        """Write the results of a single timestep to the database.

        Args:
            results (dict): The results of a single timestep

        """
        # Check that results are correct type
        parsed_results: TimestepData = TimestepData(**results)
        # Parse results to dictionary and append to buffer
        timestep_results: dict[str, Optional[float]] = parsed_results.model_dump()
        self.data_buffer.append(timestep_results)

        # Write buffer to database if it is full
        if len(self.data_buffer) == self.batch_size:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

    def write_batch(self, batch: list[TimestepData]) -> None:
        """Write a batch of results to the database.

        Args:
            batch (list): A batch of results

        """
        # Find document with sim_id and push batch
        self.results_collection.update_one(
            {"sim_id": self.sim_id}, {"$push": {"timeseries": {"$each": batch}}}
        )

    def shutdown(self) -> None:
        """Shutdown of the database:
        - Writes any remaining data in the buffer to the database
        - Closes the connection to the database.
        """
        # Write remaining data in buffer to database
        if self.data_buffer:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

        # Close connection to database
        self.client.close()
