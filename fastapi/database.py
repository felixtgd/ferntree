import os

from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi


# Load config from .env file:
load_dotenv()
MONGODB_URI = os.environ["MONGODB_URI"]


class DBClient:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URI, server_api=ServerApi("1"))
        self.db = self.client.sample_mflix
        self.movies = self.db.movies

    async def list_databases(self):
        print("Databases:")
        for db_info in await self.client.list_database_names():
            print(db_info)

    async def list_collections(self):
        print("Collections in sample_mflix:")
        for collection in await self.db.list_collection_names():
            print(collection)

    async def get_random_movie(self):
        print("Movie:")
        # Print a random movie from the collection
        movie = await self.movies.find_one()
        print(movie)
        # Print the title of the movie
        print(movie["title"])

    async def close(self):
        self.client.close()


# client = DBClient()
# asyncio.run(client.list_databases())
