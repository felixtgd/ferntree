import os
import certifi

from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

from components.database.models import TimestepData

# Use certifi to get the path of the CA file
ca = certifi.where()

# Load config from .env file:
scipt_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(
    scipt_dir, "../../../../.env"
)  # TODO: Improve this! Path not cool
load_dotenv(env_path)
MONGODB_URI = os.environ["MONGODB_URI"]
MONGODB_DATABASE = os.environ["MONGODB_DATABASE"]


class pyMongoClient:
    def __init__(self, sim_id: str, model_id: str):
        self.client = MongoClient(MONGODB_URI, server_api=ServerApi("1"), tlsCAFile=ca)

        self.db = self.client[MONGODB_DATABASE]
        self.results_collection = self.db["sim_results_ts"]
        self.results_collection.create_index("sim_id", unique=True)
        self.results_collection.create_index("model_id", unique=True)
        self.results_collection.update_one(
            {"sim_id": sim_id},
            {
                "$set": {
                    "model_id": model_id,
                    "run_time": datetime.now().isoformat(),
                }
            },
            upsert=True,
        )

        self.sim_id = sim_id

        self.batch_size = 1000
        self.data_buffer = []

    def load_config(self) -> dict:
        # Load sim config from database
        collection = self.db["simulations"]
        result = collection.find_one({"_id": ObjectId(self.sim_id)})

        return result

    def get_load_profile(self, profile_id: int) -> list:
        # Get load profile for baseload from database
        collection = self.db["loadprofiles"]
        result = collection.find_one({"profile_id": profile_id})

        return result["load_profile"]

    def write_timeseries_data_to_db(self, results: dict):
        # Check that results are correct type
        parsed_results = TimestepData(**results)
        # Parse results to dictionary and append to buffer
        timestep_results = parsed_results.model_dump()
        self.data_buffer.append(timestep_results)

        # Write buffer to database if it is full
        if len(self.data_buffer) == self.batch_size:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

    def write_batch(self, batch: list):
        # Find document with sim_id and push batch
        self.results_collection.update_one(
            {"sim_id": self.sim_id}, {"$push": {"timeseries": {"$each": batch}}}
        )

    def shutdown(self):
        """Shutdown of the database:
        - Writes any remaining data in the buffer to the database
        - Closes the connection to the database
        """
        # Write remaining data in buffer to database
        if self.data_buffer:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

        # Close connection to database
        self.client.close()
