import asyncio

from src.database.mongodb import MongoClient

# Create a MongoDB client
db_client: MongoClient = MongoClient()

# Clean the collections
collections: list[str] = ["model_specs", "sim_evaluation", "sim_timeseries"]


async def clean_collections(collections: list[str]) -> None:
    """Clean the collections in the database.

    Args:
        collections (list[str]): The list of collections to clean.

    """
    # Delete all documents in the collections
    for collection in collections:
        await db_client.clean_collection(collection)


# Run the function to clean the collections
asyncio.run(clean_collections(collections))
