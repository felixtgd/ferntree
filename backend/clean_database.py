import asyncio

from database.mongodb import MongoClient

# Create a MongoDB client
db_client: MongoClient = MongoClient()

# Clean the collections
collections: list[str] = ["model_specs", "sim_evaluation", "sim_timeseries"]


async def clean_collections(collections: list[str]) -> None:
    # Delete all documents in the collections
    for collection in collections:
        await db_client.clean_collection(collection)


# Run the function to clean the collections
asyncio.run(clean_collections(collections))
