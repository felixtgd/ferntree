import os
from typing import Any, Optional, Union

import certifi
from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorCursor,
    AsyncIOMotorDatabase,
)
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult
from pymongo.server_api import ServerApi

from src.database.models import (
    FinFormData,
    FinResults,
    ModelDataOut,
    SimDataIn,
    SimResultsEval,
)

# Use certifi to get the path of the CA file
ca: str = certifi.where()

# Load config from .env file:
load_dotenv("./.env")
MONGODB_URI: str = os.environ["MONGODB_URI"]
MONGODB_DATABASE: str = os.environ["MONGODB_DATABASE"]


class MongoClient:
    """A client for interacting with MongoDB using Motor for asynchronous operations.

    This class provides methods for various database operations including checking
    user existence, inserting and fetching models, updating simulation IDs, deleting
    models, and handling documents in different collections.
    """

    def __init__(self) -> None:
        """Initialize the MongoClient with the MongoDB connection.

        Uses environment variables for the MongoDB URI and database name.
        """
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(
            MONGODB_URI, server_api=ServerApi("1"), tlsCAFile=ca
        )
        self.db: AsyncIOMotorDatabase = self.client[MONGODB_DATABASE]

    async def check_user_exists(self, user_id: str) -> bool:
        """Check if a user with the given ID exists in the database.

        Args:
            user_id (str): The ID of the user to check.

        Returns:
            bool: True if the user exists, False otherwise.

        """
        query: dict[str, ObjectId] = {"_id": ObjectId(user_id)}
        db_collection: AsyncIOMotorCollection = self.db["users"]
        user: Optional[dict[str, Any]] = await db_collection.find_one(query)

        return user is not None

    async def insert_model(self, model: dict[str, Any]) -> str:
        """Insert a new model into the database.

        Args:
            model (dict[str, Any]): The model data to insert.

        Returns:
            str: The ID of the inserted model.

        """
        db_collection: AsyncIOMotorCollection = self.db["models"]
        await db_collection.create_index("user_id", unique=False)

        result: InsertOneResult = await db_collection.insert_one(model)
        return str(result.inserted_id)

    async def fetch_models(self, user_id: str) -> list[ModelDataOut]:
        """Fetch all models associated with a given user ID.

        Args:
            user_id (str): The ID of the user whose models to fetch.

        Returns:
            list[ModelDataOut]: A list of ModelDataOut objects representing
                                the user's models.

        """
        query: dict[str, str] = {"user_id": user_id}
        db_collection: AsyncIOMotorCollection = self.db["models"]
        cursor: AsyncIOMotorCursor = db_collection.find(query)

        models: list[ModelDataOut] = [
            ModelDataOut(**model, model_id=str(model["_id"])) async for model in cursor
        ]

        return models

    async def update_sim_id_of_model(self, model_id: str, sim_id: str) -> bool:
        """Update the simulation ID of a specific model.

        Args:
            model_id (str): The ID of the model to update.
            sim_id (str): The new simulation ID.

        Returns:
            bool: True if the update was acknowledged, False otherwise.

        """
        query: dict[str, ObjectId] = {"_id": ObjectId(model_id)}
        db_collection: AsyncIOMotorCollection = self.db["models"]
        doc_updated: UpdateResult = await db_collection.update_one(
            query, {"$set": {"sim_id": sim_id}}
        )
        acknowledged: bool = doc_updated.acknowledged

        return acknowledged

    async def delete_model(self, model_id: str) -> bool:
        """Delete a model and all associated documents from various collections.

        Args:
            model_id (str): The ID of the model to delete.

        Returns:
            bool: True if the deletion was acknowledged, False otherwise.

        """
        query_model_id: dict[str, ObjectId] = {"_id": ObjectId(model_id)}
        db_collection_models: AsyncIOMotorCollection = self.db["models"]
        delete_result: DeleteResult = await db_collection_models.delete_one(
            query_model_id
        )

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
        """Fetch a specific model by its ID.

        Args:
            model_id (str): The ID of the model to fetch.

        Returns:
            ModelDataOut: The model data.

        Raises:
            RuntimeError: If the model with the given ID is not found.

        """
        query: dict[str, ObjectId] = {"_id": ObjectId(model_id)}
        db_collection: AsyncIOMotorCollection = self.db["models"]
        model: Optional[dict[str, Any]] = await db_collection.find_one(query)

        if model is None:
            raise RuntimeError(f"Failed to fetch model with ID {model_id}")
        else:
            return ModelDataOut(**model, model_id=str(model["_id"]))

    async def fetch_document(
        self, collection: str, model_id: str
    ) -> Optional[dict[str, Any]]:
        """Fetch a document from a specified collection for a given model ID.

        Args:
            collection (str): Name of the collection to fetch data from.
            model_id (str): ID of the model.

        Returns:
            Optional[dict[str, Any]]: The fetched document, or None if not found.

        """
        query: dict[str, str] = {"model_id": model_id}
        db_collection: AsyncIOMotorCollection = self.db[collection]
        doc: Optional[dict[str, Any]] = await db_collection.find_one(query)

        return doc

    async def insert_document(
        self,
        collection: str,
        document: Union[SimDataIn, SimResultsEval, FinFormData, FinResults],
    ) -> str:
        """Insert or replace a document in a specified collection.

        Args:
            collection (str): Name of the collection to insert the document into.
            document (Union[SimDataIn, SimResultsEval, FinFormData, FinResults]):
                The document to insert.

        Returns:
            str: The ID of the inserted or updated document.

        Raises:
            RuntimeError: If the document doesn't have a model_id attribute or
                            if the insertion fails.

        """
        try:
            model_id: str = document.model_id
        except AttributeError:
            raise RuntimeError("Document must have a model_id attribute.")

        query: dict[str, str] = {"model_id": model_id}
        db_collection: AsyncIOMotorCollection = self.db[collection]

        await db_collection.create_index("model_id", unique=True)

        result: UpdateResult = await db_collection.replace_one(
            query, document.model_dump(), upsert=True
        )

        if not result.acknowledged:
            raise RuntimeError(
                "Failed to insert or update the document in the database."
            )

        return str(result.upserted_id)

    async def clean_collection(self, collection: str) -> None:
        """Delete all documents in a specified collection.

        Args:
            collection (str): Name of the collection to clean.

        """
        db_collection: AsyncIOMotorCollection = self.db[collection]
        await db_collection.delete_many({})
