import os
import certifi

from dotenv import load_dotenv
from bson import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
    AsyncIOMotorCursor,
)
from pymongo.server_api import ServerApi
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from typing import Any, Optional

from backend.database.models import (
    ModelDataOut,
    SimTimestep,
    SimResultsEval,
    FinFormData,
    FinResults,
)


# Use certifi to get the path of the CA file
ca: str = certifi.where()

# Load config from .env file:
load_dotenv("./.env")
MONGODB_URI: str = os.environ["MONGODB_URI"]
MONGODB_DATABASE: str = os.environ["MONGODB_DATABASE"]


class MongoClient:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(
            MONGODB_URI, server_api=ServerApi("1"), tlsCAFile=ca
        )
        self.db: AsyncIOMotorDatabase = self.client[MONGODB_DATABASE]

    async def check_user_exists(self, user_id: str) -> bool:
        query: dict[str, ObjectId] = {"_id": ObjectId(user_id)}
        db_collection: AsyncIOMotorCollection = self.db["users"]
        user: Optional[dict[str, Any]] = await db_collection.find_one(query)

        if user is None:
            return False
        else:
            return True

    async def insert_model(
        self,
        model: dict[str, Any],
    ) -> str:
        # Each model has a unique user_id, a user can have multiple models

        # Create an index on the user_id field
        db_collection: AsyncIOMotorCollection = self.db["models"]
        await db_collection.create_index("user_id", unique=False)

        # Insert model in database
        result: InsertOneResult = await db_collection.insert_one(model)
        model_id: str = str(result.inserted_id)

        return model_id

    async def insert_sim_data(
        self,
        collection: str,
        sim_data: dict[str, Any],
    ) -> str:
        # One-to-one relationship between model and simulation
        query: dict[str, str] = {"model_id": sim_data["model_id"]}

        # Create an index on the model_id field
        db_collection: AsyncIOMotorCollection = self.db[collection]
        await db_collection.create_index("model_id", unique=True)

        # Fetch the existing document's ID if it exists
        existing_document: Optional[dict[str, Any]] = await db_collection.find_one(
            query
        )
        existing_id: Optional[str] = (
            str(existing_document["_id"]) if existing_document else None
        )

        # Insert or replace document in database
        result: UpdateResult = await db_collection.replace_one(
            query, sim_data, upsert=True
        )

        # If the document was inserted, result.upserted_id will be set
        if result.upserted_id:
            inserted_id: str = str(result.upserted_id)
            return inserted_id
        elif existing_id:
            return existing_id
        else:
            raise RuntimeError(
                "Failed to insert or update the document in the database."
            )

    async def fetch_models(self, user_id: str) -> list[ModelDataOut]:
        # Fetch all models of the user
        query: dict[str, str] = {"user_id": user_id}
        db_collection: AsyncIOMotorCollection = self.db["models"]
        cursor: AsyncIOMotorCursor = db_collection.find(query)

        models: list[ModelDataOut] = [
            ModelDataOut(**model, model_id=str(model["_id"])) async for model in cursor
        ]

        return models

    async def update_sim_id_of_model(self, model_id: str, sim_id: str) -> bool:
        query: dict[str, ObjectId] = {"_id": ObjectId(model_id)}
        db_collection: AsyncIOMotorCollection = self.db["models"]
        doc_updated: UpdateResult = await db_collection.update_one(
            query, {"$set": {"sim_id": sim_id}}
        )
        acknowledged: bool = doc_updated.acknowledged
        return acknowledged

    async def delete_model(self, model_id: str) -> bool:
        # Deletethe the model from collection "models"
        query_model_id: dict[str, ObjectId] = {"_id": ObjectId(model_id)}
        db_collection_models: AsyncIOMotorCollection = self.db["models"]
        delete_result: DeleteResult = await db_collection_models.delete_one(
            query_model_id
        )

        # Delete all other docs associated with the model
        collections: list[str] = ["simulations", "sim_results_ts", "sim_results_eval"]
        for collection in collections:
            query: dict[str, str] = {"model_id": model_id}
            db_collection: AsyncIOMotorCollection = self.db[collection]
            await db_collection.delete_many(query)

        acknowledged: bool = delete_result.acknowledged
        return acknowledged

    async def fetch_model_by_id(self, model_id: str) -> ModelDataOut:
        # Find one document in the collection that matches the query
        query: dict[str, ObjectId] = {"_id": ObjectId(model_id)}
        db_collection: AsyncIOMotorCollection = self.db["models"]
        model: Optional[dict[str, Any]] = await db_collection.find_one(query)

        if model is None:
            raise RuntimeError(f"Failed to fetch model with ID {model_id}")
        else:
            model_data: ModelDataOut = ModelDataOut(**model, model_id=str(model["_id"]))
            return model_data

    async def fetch_sim_results_ts(self, model_id: str) -> list[SimTimestep]:
        # Find one document in the collection that matches the query
        query: dict[str, str] = {"model_id": model_id}
        db_collection: AsyncIOMotorCollection = self.db["sim_results_ts"]
        doc: Optional[dict[str, Any]] = await db_collection.find_one(query)

        if doc is None:
            raise RuntimeError(
                f"Failed to fetch sim results timeseries for model_id {model_id}"
            )
        else:
            sim_results_ts = [SimTimestep(**timestep) for timestep in doc["timeseries"]]
            return sim_results_ts

    async def fetch_sim_results_eval(self, model_id: str) -> Optional[SimResultsEval]:
        # Find one document in the collection that matches the query
        query: dict[str, str] = {"model_id": model_id}
        db_collection: AsyncIOMotorCollection = self.db["sim_results_eval"]
        doc: Optional[dict[str, Any]] = await db_collection.find_one(query)
        if doc is None:
            return None
        else:
            sim_results_ts: SimResultsEval = SimResultsEval(**doc)
            return sim_results_ts

    async def fetch_fin_form_data(self, model_id: str) -> Optional[FinFormData]:
        # Find one document in the collection that matches the query
        query: dict[str, str] = {"model_id": model_id}
        db_collection: AsyncIOMotorCollection = self.db["finances"]
        doc: Optional[dict[str, Any]] = await db_collection.find_one(query)
        if doc is None:
            return None
        else:
            fin_form_data: FinFormData = FinFormData(**doc)
            return fin_form_data

    async def insert_fin_form_data(self, fin_form_data: FinFormData) -> None:
        # Insert fin_form_data in database or replace if already exists
        query: dict[str, str] = {"model_id": fin_form_data.model_id}
        db_collection: AsyncIOMotorCollection = self.db["finances"]
        # Create index on model_id field
        await db_collection.create_index("model_id", unique=True)
        # Insert or replace document in database
        result: UpdateResult = await db_collection.replace_one(
            query, fin_form_data.model_dump(), upsert=True
        )
        acknowledged: bool = result.acknowledged
        if not acknowledged:
            raise RuntimeError(
                "Failed to insert or update the document in the database."
            )

    async def insert_fin_results(self, fin_results: FinResults) -> None:
        # Insert fin_results in database or replace if already exists
        query: dict[str, str] = {"model_id": fin_results.model_id}
        db_collection: AsyncIOMotorCollection = self.db["fin_results"]
        # Create index on model_id field
        await db_collection.create_index("model_id", unique=True)
        # Insert or replace document in database
        result: UpdateResult = await db_collection.replace_one(
            query, fin_results.model_dump(), upsert=True
        )
        acknowledged: bool = result.acknowledged
        if not acknowledged:
            raise RuntimeError(
                "Failed to insert or update the document in the database."
            )

    async def fetch_fin_results(self, model_id: str) -> FinResults:
        # Find one document in the collection that matches the query
        query: dict[str, str] = {"model_id": model_id}
        db_collection: AsyncIOMotorCollection = self.db["fin_results"]
        doc: Optional[dict[str, Any]] = await db_collection.find_one(query)
        if doc is None:
            raise RuntimeError(f"Failed to fetch fin results for model_id {model_id}")
        else:
            fin_results: FinResults = FinResults(**doc)
            return fin_results

    async def clean_collection(self, collection: str) -> None:
        # Delete all documents in the collection
        db_collection: AsyncIOMotorCollection = self.db[collection]
        await db_collection.delete_many({})

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
