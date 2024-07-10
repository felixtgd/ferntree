import logging

from datetime import datetime
from enum import Enum
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from database.models import (
    UserInputForm,
    TimeseriesDataRequest,
    FilteredTimeseriesData,
)
from database.mongodb import MongoClient
from utils.sim_funcs import (
    process_user_input,
    run_ferntree_simulation,
    evaluate_simulation_results,
    calc_monthly_pv_gen_data,
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


@app.post("/dashboard/submit-model")
# TODO: add response_model = ... for data validation
async def pv_calc(user_input: UserInputForm):
    logger.info(
        f"\n/dashboard/submit-model --> Received request: user_input={user_input}"
    )

    # Determine user_id
    user_id = 123

    # Process user input and write to database
    model_id = await process_user_input(db_client, user_input, user_id)
    if not model_id:
        logger.error("Error processing user input")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error processing user input",
        )

    logger.info(f"\n/dashboard/submit-model --> Return Model ID: {model_id}")

    return model_id


@app.get("/dashboard/run-simulation")
async def run_simulation(model_id: str):
    logger.info(
        f"\n/dashboard/run-simulation --> Received request: model_id={model_id}"
    )
    # Fetch the model specifications
    sim_model_specs = await db_client.find_one_by_id("model_specs", model_id)
    sim_id = sim_model_specs["sim_id"]

    # Start ferntree simulation
    sim_run = await run_ferntree_simulation(sim_id, model_id)

    if sim_run:
        logger.info(f"\n/dashboard/run-simulation --> Sim {sim_id} ran successfully!")
        return {"sim_run_success": True}
    else:
        logger.info(f"\n/dashboard/run-simulation --> Sim {sim_id} failed!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error running simulation",
        )


@app.get("/dashboard/simulation-results")
async def fetch_simulation_results(model_id: str):
    logger.info(
        f"\n/dashboard/simulation-results --> Received request: model_id={model_id}"
    )

    # Fetch the model specifications TODO: stupid to do this again here!!!
    sim_model_specs = await db_client.find_one_by_id("model_specs", model_id)
    sim_id = sim_model_specs["sim_id"]

    # Evaluate simulation results
    sim_eval_id, sim_evaluation = await evaluate_simulation_results(
        db_client, sim_id, sim_model_specs["sim_model_specs"]
    )
    if not sim_evaluation or not sim_eval_id:
        logger.error(
            f"Error evaluating simulation results. model_id={model_id}, sim_id={sim_id}, sim_eval_id={sim_eval_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error evaluating simulation results",
        )

    logger.info(
        f"\n/dashboard/simulation-results --> Return Simulation Evaluation: {sim_evaluation}"
    )
    return sim_evaluation


@app.post("/dashboard/sim-timeseries-data")
async def fetch_timeseries_data(request_body: TimeseriesDataRequest):
    logger.info(
        f"\n/dashboard/sim-timeseries-data --> Received request: {request_body}"
    )
    try:
        start_date = datetime.fromisoformat(request_body.start_date).timestamp()
        end_date = datetime.fromisoformat(request_body.end_date).timestamp()
    except ValueError as e:
        logger.error(f"Error parsing datetime: {e}")
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    # Fetch the timeseries data of the simulation
    timeseries_data = await db_client.fetch_timeseries_data(sim_id=request_body.sim_id)

    # Filter the timeseries data to only include data within the given date range
    filtered_timeseries_data = [
        FilteredTimeseriesData(**data)
        for data in timeseries_data
        if start_date <= data["time"] <= end_date
    ]

    formatted_timeseries_data = format_timeseries_data(filtered_timeseries_data)

    logger.info(
        f"\n/dashboard/sim-timeseries-data --> Return timeseries data: {len(formatted_timeseries_data)} data points"
    )

    return formatted_timeseries_data  # TODO: define data model for response


@app.get("/dashboard/pv-monthly-gen")
async def fetch_pv_monthly_gen_data(model_id: str):
    logger.info(
        f"\n/dashboard/pv-monthly-gen --> Received request: model_id={model_id}"
    )
    # Fetch the model specifications TODO: stupid to do this again here!!!
    sim_model_specs = await db_client.find_one_by_id("model_specs", model_id)
    sim_id = sim_model_specs["sim_id"]

    # Fetch the timeseries data of the simulation
    timeseries_data = await db_client.fetch_timeseries_data(sim_id=sim_id)

    # Calculate the monthly PV generation data
    monthly_pv_gen_data = await calc_monthly_pv_gen_data(timeseries_data)

    logger.info(
        f"\n/dashboard/pv-monthly-gen --> Return Monthly PV Generation Data: {monthly_pv_gen_data}"
    )
    return monthly_pv_gen_data
