import os

from dotenv import load_dotenv

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi


# Load config from .env file:
load_dotenv()
MONGODB_URI = os.environ["MONGODB_URI"]


async def ping_server():
    # Set the Stable API version when creating a new client
    client = AsyncIOMotorClient(MONGODB_URI, server_api=ServerApi("1"))

    # Send a ping to confirm a successful connection
    try:
        await client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    # List all the databases in the cluster:
    print("Databases:")
    for db_info in await client.list_database_names():
        print(db_info)

    db = client.sample_mflix
    print("Collections in sample_mflix:")
    for collection in await db.list_collection_names():
        print(collection)

    movies = db.movies
    print("Movie:")
    # Print a random movie from the collection
    movie = await movies.find_one()
    print(movie)
    # Print the title of the movie
    print(movie["title"])


asyncio.run(ping_server())
