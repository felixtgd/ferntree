from pvgis_api import get_solar_data_for_coordinates
from geolocator import get_location_coordinates
from models import PvgisInputData, SimTimeSeriesDoc
from database import MongoClient
from datetime import datetime
import asyncio

location = "Ferntree Gully, Victoria, Australia"
coordinates = get_location_coordinates(location)
print(coordinates)

solar_data = get_solar_data_for_coordinates(coordinates)
# print(solar_data[:2])

parsed_solar_data = [PvgisInputData(**item) for item in solar_data]
print(parsed_solar_data[:2])

# Simulation specifications
user_id = 123
created_at = datetime.now().isoformat()
document_solar_data = SimTimeSeriesDoc(
    user_id=user_id,
    created_at=created_at,
    location=location,
    coordinates=coordinates,
    timeseries_data=parsed_solar_data,
)


async def main():
    # Write parsed data to MongoDB
    client = MongoClient(database_name="ferntree_db", collection_name="simulation_coll")
    sim_id = await client.insert_one(document_solar_data.model_dump())

    # Read data from MongoDB
    data = await client.find_one({"_id": sim_id})
    print(data)


asyncio.run(main())
