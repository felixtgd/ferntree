import os
import certifi

from dotenv import load_dotenv
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from typing import Union

from backend.database.models import ModelData


# Use certifi to get the path of the CA file
ca = certifi.where()

# Load config from .env file:
load_dotenv("./.env")
MONGODB_URI = os.environ["MONGODB_URI"]
MONGODB_DATABASE = os.environ["MONGODB_DATABASE"]


class MongoClient:
    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(
            MONGODB_URI, server_api=ServerApi("1"), tlsCAFile=ca
        )
        self.db = self.client[MONGODB_DATABASE]

    async def check_user_exists(self, user_id: str) -> bool:
        query = {"_id": ObjectId(user_id)}
        collection = self.db["users"]
        user = await collection.find_one(query)

        if user is None:
            return False
        else:
            return True

    async def insert_one(self, collection: str, document: dict) -> Union[str, None]:
        # Insert a document into the collection
        db_collection = self.db[collection]
        result = await db_collection.insert_one(document)

        if result.acknowledged:
            return str(result.inserted_id)
        else:
            return None

    async def fetch_models(self, user_id: str) -> list[ModelData]:
        # Fetch all models of the user
        query = {"user_id": user_id}
        db_collection = self.db["models"]
        cursor = db_collection.find(query)

        models = [model async for model in cursor]

        return models

    # --------- OLD SHIT -------------

    async def find_one_by_id(self, collection: str, id: str):
        query = {"_id": ObjectId(id)}
        # Find one document in the collection that matches the query
        collection = self.db[collection]
        document = await collection.find_one(query)

        # Return the document
        return document

    async def clean_collection(self, collection: str):
        # Delete all documents in the collection
        collection = self.db[collection]
        await collection.delete_many({})

    async def fetch_timeseries_data(self, sim_id: str) -> list[dict]:
        # Fetch the timeseries data of the simulation matching the given date range
        collection = self.db["sim_timeseries"]
        query = {"_id": ObjectId(sim_id)}

        document = await collection.find_one(query)

        timeseries_data = document["timeseries_data"]

        return timeseries_data

    async def close(self):
        self.client.close()
