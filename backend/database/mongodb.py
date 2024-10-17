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

from typing import Any, Optional, Union

from backend.database.models import (
    ModelDataOut,
    SimDataIn,
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
        # Delete the the model from collection "models"
        query_model_id: dict[str, ObjectId] = {"_id": ObjectId(model_id)}
        db_collection_models: AsyncIOMotorCollection = self.db["models"]
        delete_result: DeleteResult = await db_collection_models.delete_one(
            query_model_id
        )

        # Delete all other docs associated with the model
        collections: list[str] = [
            "simulations",
            "sim_results_ts",
            "sim_results_eval",
            "finances",
            "fin_results",
        ]
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

    async def fetch_document(
        self, collection: str, model_id: str
    ) -> Optional[dict[str, Any]]:
        """Fetch document from the specified collection for the given model_id.

        Args:
            collection (str): Name of the collection to fetch data from
            model_id (str): ID of the model

        Returns:
            dict: Data fetched from the collection
        """

        # Find one document in the collection that matches the query
        query: dict[str, str] = {"model_id": model_id}
        db_collection: AsyncIOMotorCollection = self.db[collection]
        doc: Optional[dict[str, Any]] = await db_collection.find_one(query)

        return doc

    async def insert_document(
        self,
        collection: str,
        document: Union[SimDataIn, SimResultsEval, FinFormData, FinResults],
    ) -> str:
        try:
            model_id: str = document.model_id
        except AttributeError:
            raise RuntimeError("Document must have a model_id attribute.")

        # Insert document in database or replace if already exists
        query: dict[str, str] = {"model_id": model_id}
        db_collection: AsyncIOMotorCollection = self.db[collection]

        # Create index on model_id field
        await db_collection.create_index("model_id", unique=True)

        # Insert or replace document in database
        result: UpdateResult = await db_collection.replace_one(
            query, document.model_dump(), upsert=True
        )
        acknowledged: bool = result.acknowledged

        if not acknowledged:
            raise RuntimeError(
                "Failed to insert or update the document in the database."
            )

        return str(result.upserted_id)

    async def clean_collection(self, collection: str) -> None:
        # Delete all documents in the collection
        db_collection: AsyncIOMotorCollection = self.db[collection]
        await db_collection.delete_many({})
