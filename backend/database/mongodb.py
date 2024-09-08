import os
import certifi

from dotenv import load_dotenv
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from typing import Union

from backend.database.models import ModelDataOut, SimTimestep


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
        db_collection = self.db["users"]
        user = await db_collection.find_one(query)

        if user is None:
            return False
        else:
            return True

    async def insert_one(
        self,
        collection: str,
        document: dict,
        index: Union[str, None] = None,
        unique: bool = False,
    ) -> Union[str, None]:
        # Insert a document into the collection
        db_collection = self.db[collection]
        if index is not None:
            await db_collection.create_index(index, unique=unique)

        # Define the query to check for existing document
        query = {index: document[index]} if index else {}

        # Fetch the existing document's ID if it exists
        existing_document = await db_collection.find_one(query, {"_id": 1})
        existing_id = str(existing_document["_id"]) if existing_document else None

        # Replace the document if it exists, or insert a new one if it doesn't
        result = await db_collection.replace_one(query, document, upsert=True)

        if result.upserted_id:
            return str(result.upserted_id)
        elif result.modified_count > 0:
            return existing_id
        else:
            return None

    async def fetch_models(self, user_id: str) -> list[ModelDataOut]:
        # Fetch all models of the user
        query = {"user_id": user_id}
        db_collection = self.db["models"]
        cursor = db_collection.find(query)

        models = [
            ModelDataOut(**model, model_id=str(model["_id"])) async for model in cursor
        ]

        return models

    async def update_sim_id_of_model(self, model_id: str, sim_id: str):
        query = {"_id": ObjectId(model_id)}
        db_collection = self.db["models"]
        doc_updated = await db_collection.update_one(
            query, {"$set": {"sim_id": sim_id}}
        )

        return doc_updated.acknowledged

    async def delete_model(self, model_id: str):
        query = {"_id": ObjectId(model_id)}
        db_collection = self.db["models"]
        delete_result = await db_collection.delete_one(query)

        return delete_result.acknowledged

    async def fetch_model_by_id(self, model_id: str) -> ModelDataOut:
        # Find one document in the collection that matches the query
        query = {"_id": ObjectId(model_id)}
        db_collection = self.db["models"]
        model = await db_collection.find_one(query)

        model = ModelDataOut(**model, model_id=str(model["_id"]))

        return model

    async def fetch_sim_results_by_id(self, model_id: str) -> list[SimTimestep]:
        # Find one document in the collection that matches the query
        query = {"model_id": model_id}
        db_collection = self.db["sim_results_ts"]
        doc = await db_collection.find_one(query)
        sim_results_ts = [SimTimestep(**timestep) for timestep in doc["timeseries"]]

        return sim_results_ts

    # --------- OLD SHIT -------------

    # async def find_one_by_id(self, collection: str, id: str):
    #     query = {"_id": ObjectId(id)}
    #     # Find one document in the collection that matches the query
    #     collection = self.db[collection]
    #     document = await collection.find_one(query)

    #     # Return the document
    #     return document

    # async def clean_collection(self, collection: str):
    #     # Delete all documents in the collection
    #     collection = self.db[collection]
    #     await collection.delete_many({})

    # async def fetch_timeseries_data(self, sim_id: str) -> list[dict]:
    #     # Fetch the timeseries data of the simulation matching the given date range
    #     collection = self.db["sim_timeseries"]
    #     query = {"_id": ObjectId(sim_id)}

    #     document = await collection.find_one(query)

    #     timeseries_data = document["timeseries_data"]

    #     return timeseries_data

    # async def close(self):
    #     self.client.close()
