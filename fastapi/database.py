import motor.motor_asyncio

from models import SolarIrradiationData

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client.SimData
collection = db.SolarIrradiation


async def insert_data(data: SolarIrradiationData):
    await collection.insert_one(data.model_dump())
    return True


async def get_data():
    data = []
    async for doc in collection.find():
        data.append(doc)
    return data
