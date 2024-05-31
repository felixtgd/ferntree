import os
import certifi

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

from database.models import TimestepData

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
    def __init__(self, model_id: str, sim_id: str):
        self.client = MongoClient(MONGODB_URI, server_api=ServerApi("1"), tlsCAFile=ca)

        self.db = self.client[MONGODB_DATABASE]

        self.model_id = ObjectId(model_id)
        self.sim_id = ObjectId(sim_id)

        self.batch_size = 1000
        self.data_buffer = []

    def load_config(self) -> dict:
        # Load model specifications from database
        collection = self.db["model_specs"]
        result = collection.find_one({"_id": self.model_id})

        return result

    def load_simulation_input(self) -> dict:
        # Load simulation input data from database
        collection = self.db["sim_timeseries"]
        result = collection.find_one({"_id": self.sim_id})

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
        collection = self.db["sim_timeseries"]
        # Find document with id sim_id and push batch to timeseries_data
        collection.update_one(
            {"_id": self.sim_id}, {"$push": {"timeseries_data": {"$each": batch}}}
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

        # Delete input arrays T_amb and G_i from document
        collection = self.db["sim_timeseries"]
        collection.update_one(
            {"_id": self.sim_id}, {"$unset": {"T_amb": "", "G_i": ""}}
        )

        # Close connection to database
        self.client.close()
