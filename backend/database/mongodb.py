import os
import certifi

from dotenv import load_dotenv
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

# from pymongo.errors import DuplicateKeyError
from typing import Union

from backend.database.models import ModelDataOut, SimTimestep, SimResultsEval


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

    async def insert_model(
        self,
        model: dict,
    ) -> str:
        # Each model has a unique user_id, a user can have multiple models

        # Create an index on the user_id field
        db_collection = self.db["models"]
        await db_collection.create_index("user_id", unique=False)

        # Insert model in database
        result = await db_collection.insert_one(model)
        model_id = str(result.inserted_id)

        return model_id

    async def insert_sim_data(
        self,
        collection: str,
        sim_data: dict,
    ) -> str:
        # One-to-one relationship between model and simulation
        query = {"model_id": sim_data["model_id"]}

        # Create an index on the model_id field
        db_collection = self.db[collection]
        await db_collection.create_index("model_id", unique=True)

        # Fetch the existing document's ID if it exists
        existing_document = await db_collection.find_one(query)
        existing_id = str(existing_document["_id"]) if existing_document else None

        # Insert or replace document in database
        result = await db_collection.replace_one(query, sim_data, upsert=True)

        # If the document was inserted, result.upserted_id will be set
        inserted_id = str(result.upserted_id) if result.upserted_id else existing_id

        return inserted_id

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
        # Deletethe the model from collection "models"
        query = {"_id": ObjectId(model_id)}
        db_collection = self.db["models"]
        delete_result = await db_collection.delete_one(query)

        # Delete all other docs associated with the model
        collections = ["simulations", "sim_results_ts", "sim_results_eval"]
        for collection in collections:
            query = {"model_id": model_id}
            db_collection = self.db[collection]
            await db_collection.delete_many(query)

        return delete_result.acknowledged

    async def fetch_model_by_id(self, model_id: str) -> ModelDataOut:
        # Find one document in the collection that matches the query
        query = {"_id": ObjectId(model_id)}
        db_collection = self.db["models"]
        model = await db_collection.find_one(query)

        model = ModelDataOut(**model, model_id=str(model["_id"]))

        return model

    async def fetch_sim_results_ts(self, model_id: str) -> list[SimTimestep]:
        # Find one document in the collection that matches the query
        query = {"model_id": model_id}
        db_collection = self.db["sim_results_ts"]
        doc = await db_collection.find_one(query)
        sim_results_ts = [SimTimestep(**timestep) for timestep in doc["timeseries"]]

        return sim_results_ts

    async def fetch_sim_results_eval(
        self, model_id: str
    ) -> Union[SimResultsEval, None]:
        # Find one document in the collection that matches the query
        query = {"model_id": model_id}
        db_collection = self.db["sim_results_eval"]
        doc = await db_collection.find_one(query)
        if doc:
            sim_results_ts = SimResultsEval(**doc)
            return sim_results_ts
        else:
            return None

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
