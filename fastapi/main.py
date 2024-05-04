import logging
import os
import subprocess

from datetime import datetime
from enum import Enum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.models import SimModelSpecs, PvgisInputData, SimTimeSeriesDoc
from database.mongodb import MongoClient
from solar_data import pvgis_api


class RoofTilt(int, Enum):
    flat = 0
    tilted30 = 30
    tilted45 = 45


class RoofAzimuth(int, Enum):
    south = 0
    south_east = -45
    south_west = 45
    east = -90
    west = 90
    north_east = -135
    north_west = 135
    north = 180


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend_logger")

# Create a FastAPI instance
app = FastAPI()

# Create a MongoDB client
db_client = MongoClient(database_name="ferntree_db", collection_name="simulation_coll")

# Configure CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.post("/dashboard/pv-calc")
@app.get("/dashboard/pv-calc")
async def pv_calc(
    sim_model: SimModelSpecs = SimModelSpecs(
        **{
            "location": "Ferntree Gully, Victoria, Australia",
            "electr_cons": 10,
            "roof_incl": RoofTilt.tilted30,
            "roof_azimuth": RoofAzimuth.south,
            "peak_power": 5,
            "battery_cap": 10,
            "elec_price": 0.25,
            "down_payment": 1000,
            "pay_off_rate": 0.1,
            "interest_rate": 5,
        }
    ),
):
    # Get address, roof azimuth and tilt from model specs
    location = sim_model.location
    roof_azimuth = sim_model.roof_azimuth
    roof_incl = sim_model.roof_incl

    # Pass parameters to pvgis_api to query solar data for sim input
    solar_data, coordinates = pvgis_api.get_solar_data_for_location(
        location, roof_azimuth, roof_incl
    )
    parsed_solar_data = [PvgisInputData(**item) for item in solar_data]

    # Write sim input data and model specs as one document to simulation_coll in MongoDB, return sim_id
    user_id = 123
    loadprofile_id = 1
    created_at = datetime.now().isoformat()
    document_solar_data = SimTimeSeriesDoc(
        user_id=user_id,
        created_at=created_at,
        location=location,
        coordinates=coordinates,
        loadprofile_id=loadprofile_id,
        timeseries_data=parsed_solar_data,
    )
    sim_id = await db_client.insert_one(document_solar_data.model_dump())

    # Start ferntree simulation, pass sim_id to sim via args
    script_dir = os.path.dirname(__file__)
    ferntree_sim_dir = os.path.join(script_dir, "../sim/ferntree/")
    command = ["python", "ferntree.py", "--sim_id", sim_id]
    subprocess.run(command, cwd=ferntree_sim_dir)

    return {"status": "Simulation finished"}

    # Read sim results from db and calculate system KPIs

    # Compute financial perfomance with model_specs and system KPIs, write results to financial collection

    # Add financial KPIs to results, store all KPIs and model specs as one document in results collection

    # return {"status": "Simulation started", "model": sim_model.model_dump()}
