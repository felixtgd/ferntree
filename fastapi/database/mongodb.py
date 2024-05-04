import os

from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import certifi

# Use certifi to get the path of the CA file
ca = certifi.where()

# Load config from .env file:
load_dotenv("../.env")
MONGODB_URI = os.environ["MONGODB_URI"]


class MongoClient:
    def __init__(self, database_name: str, collection_name: str):
        self.client = AsyncIOMotorClient(
            MONGODB_URI, server_api=ServerApi("1"), tlsCAFile=ca
        )
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    async def insert_one(self, document):
        # Insert a document into the collection
        result = await self.collection.insert_one(document)
        # Return the _id of the inserted document which was generated by MongoDB
        return result.inserted_id

    async def find_one(self, query):
        return await self.collection.find_one(query)

    async def close(self):
        self.client.close()


# client = DBClient()
# asyncio.run(client.list_databases())
