import logging

from datetime import datetime
from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database.models import (
    SimUserInputForm,
    TimeseriesDataRequest,
)
from database.mongodb import MongoClient
from utils.sim_funcs import (
    process_sim_user_input,
    start_ferntree_simulation,
    evaluate_simulation_results,
)
from utils.data_model_helpers import format_timeseries_data


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


@app.post("/dashboard/pv-calc")  # TODO: add response_model = ... for data validation
async def pv_calc(sim_user_input: SimUserInputForm):
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

    # Evaluate simulation results
    sim_eval_id, sim_evaluation = await evaluate_simulation_results(
        db_client, sim_id, sim_user_input
    )

    logger.info(
        f"Total execution time: {(datetime.now() - starttime).total_seconds():.2f} seconds"
    )

    return sim_evaluation


@app.post("/dashboard/fetch-timeseries-data")
async def fetch_timeseries_data(request_body: TimeseriesDataRequest):
    logger.info(f"\nReceived request for timeseries data: {request_body}")
    try:
        start_date = datetime.fromisoformat(request_body.start_date).timestamp()
        end_date = datetime.fromisoformat(request_body.end_date).timestamp()
    except ValueError as e:
        logger.error(f"Error parsing datetime: {e}")
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    timeseries_data = await db_client.fetch_timeseries_data(
        collection="sim_timeseries",
        sim_id=request_body.sim_id,
        start_date=start_date,
        end_date=end_date,
    )

    formatted_timeseries_data = format_timeseries_data(timeseries_data)

    return formatted_timeseries_data  # TODO: define data model for response
