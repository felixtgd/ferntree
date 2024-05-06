import logging
import pandas as pd

from datetime import datetime
from enum import Enum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.models import (
    SimUserInputForm,
)
from database.mongodb import MongoClient
from utils.user_input_funcs import process_sim_user_input, start_ferntree_simulation


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


# Set up logger
LOGGERNAME = "fastapi_logger"
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(LOGGERNAME)

# Create a FastAPI instance
app = FastAPI()

# Create a MongoDB client
db_client = MongoClient()

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
    sim_user_input: SimUserInputForm = SimUserInputForm(
        **{
            "location": "London, United Kingdom",  # "Aarau, Switzerland" "Ferntree Gully, Victoria, Australia"
            "electr_cons": 3000,
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
    starttime = datetime.now()

    logger.info(f"\nReceived request: {sim_user_input}")

    # Determine user_id
    user_id = 123

    # Process user input and write to database
    sim_id, model_id = await process_sim_user_input(db_client, sim_user_input, user_id)

    # Start ferntree simulation
    sim_run = await start_ferntree_simulation(sim_id, model_id)
    if not sim_run:
        return {"status": "Ferntree simulation failed."}

    # Read sim results from db and calculate system KPIs
    sim_results = await db_client.find_one_by_id("simulation_timeseries", sim_id)

    sim_results_df = pd.DataFrame(sim_results["timeseries_data"])
    # Set time column to datetime, measured in seconds
    sim_results_df["time"] = pd.to_datetime(sim_results_df["time"], unit="s")
    # Set time column as index
    sim_results_df.set_index("time", inplace=True)
    print(sim_results_df.head(24))

    # Compute financial perfomance with model_specs and system KPIs, write results to financial collection

    # Add financial KPIs to results, store all KPIs and model specs as one document in results collection

    # return {"status": "Simulation started", "model": sim_model.model_dump()}

    logger.info(
        f"Total execution time: {(datetime.now() - starttime).total_seconds():.2f} seconds"
    )

    return {"status": "Simulation finished"}
