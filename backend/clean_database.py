import asyncio

from database.mongodb import MongoClient

# Create a MongoDB client
db_client = MongoClient()

# Clean the collections
collections = ["model_specs", "sim_evaluation", "sim_timeseries"]


async def clean_collections(collections):
    # Delete all documents in the collections
    for collection in collections:
        await db_client.clean_collection(collection)


# Run the function to clean the collections
asyncio.run(clean_collections(collections))
