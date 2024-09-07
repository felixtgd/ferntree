import os
import logging

from dotenv import load_dotenv

# from datetime import datetime

# from enum import Enum
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from backend.database.models import (
    ModelDataIn,
    ModelDataOut,
    SimDataIn,
    SimResultsEval,
    # EnergyKPIs,
    # PVMonthlyGen,
    # UserInputForm,
    # TimeseriesDataRequest,
    # FilteredTimeseriesData,
)
from backend.database.mongodb import MongoClient
from backend.utils.sim_funcs import (
    get_sim_input_data,
    # process_user_input,
    run_ferntree_simulation,
    eval_sim_results,
    # evaluate_simulation_results,
    # calc_monthly_pv_gen_data,
)

# from backend.utils.data_model_helpers import format_timeseries_data
from backend.utils.auth_funcs import check_user_exists


# class RoofTilt(int, Enum):
#     flat = 0
#     tilted30 = 30
#     tilted45 = 45


# class RoofAzimuth(int, Enum):
#     south = 0
#     south_east = -45
#     south_west = 45
#     east = -90
#     west = 90
#     north_east = -135
#     north_west = 135
#     north = 180


# Set up logger
LOGGERNAME = "fastapi_logger"
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(LOGGERNAME)

# Create a FastAPI instance
app = FastAPI()

# Create a MongoDB client
db_client = MongoClient()

# Load config from .env file:
load_dotenv("./.env")
FRONTEND_BASE_URI = os.environ["FRONTEND_BASE_URI"]

# Configure CORS
origins = [
    FRONTEND_BASE_URI,
    # "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/workspace/models/submit-model", response_model=str)
@check_user_exists(db_client)
async def submit_model(user_id: str, model_data: ModelDataIn):
    logger.info(
        f"\nPOST:\t/workspace/models/submit-model --> Received request: model_data={model_data}"
    )

    # Insert model data into database
    model_id = await db_client.insert_one(
        "models", model_data.model_dump(), index="user_id"
    )
    if model_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error inserting model data into database.",
        )

    logger.info(
        f"POST:\t/workspace/models/submit-model --> Return Model ID: {model_id}"
    )

    return model_id


@app.get("/workspace/models/fetch-models", response_model=list[ModelDataOut])
@check_user_exists(db_client)
async def fetch_models(user_id: str):
    logger.info(
        f"GET:\t/workspace/models/fetch-models --> Received request: user_id={user_id}"
    )

    # Fetch all models of the user
    models = await db_client.fetch_models(user_id)

    logger.info(f"GET:\t/workspace/models/fetch-models --> Return {len(models)} models")

    return models


@app.delete("/workspace/models/delete-model", response_model=str)
@check_user_exists(db_client)
async def delete_model(user_id: str, model_id: str):
    logger.info(
        f"DELETE:\t/workspace/models/delete-model --> Received request: user_id={user_id}, model_id={model_id}"
    )

    # Delete the model
    delete_result_acknowledged = await db_client.delete_model(model_id)
    if not delete_result_acknowledged:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with ID {model_id} not found.",
        )

    logger.info(
        f"DELETE:\t/workspace/models/delete-model --> Deleted model with ID: {model_id}"
    )

    return model_id


@app.get("/workspace/simulations/run-sim", response_model=dict[str, bool])
@check_user_exists(db_client)
async def run_simulation(user_id: str, model_id: str):
    logger.info(
        f"GET:\t/workspace/simulations/run-sim --> Received request: user_id={user_id}, model_id={model_id}"
    )

    # Fetch model data from database
    model_data: ModelDataOut = await db_client.fetch_model_by_id(model_id)

    # Get simulation input data
    sim_input_data: SimDataIn = await get_sim_input_data(model_data)

    # Insert simulation input data into database
    sim_id = await db_client.insert_one(
        "simulations", sim_input_data.model_dump(), index="model_id", unique=True
    )
    if sim_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error inserting sim data into database.",
        )

    # Run the simulation
    sim_run: bool = await run_ferntree_simulation(sim_id, model_id)

    if sim_run:
        logger.info(
            f"GET:\t/workspace/simulations/run-simulation --> Sim {sim_id} ran successfully!"
        )
        return {"run_successful": True}
    else:
        logger.info(
            f"ERROR:\t/workspace/simulations/run-simulation --> Sim {sim_id} failed!"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error running simulation",
        )


@app.get("/workspace/simulations/fetch-sim-results", response_model=SimResultsEval)
@check_user_exists(db_client)
async def fetch_sim_results(user_id: str, model_id: str):
    logger.info(
        f"GET:\t/workspace/simulations/fetch-sim-results --> Received request: user_id={user_id}, model_id={model_id}"
    )

    sim_results_eval: SimResultsEval = await eval_sim_results(db_client, model_id)
    await db_client.insert_one(
        "sim_results_eval", sim_results_eval.model_dump(), index="model_id"
    )

    logger.info("SimResultEval:")
    logger.info(sim_results_eval)

    return sim_results_eval


# -------------- OLD SHIT -----------------
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


# @app.post("/dashboard/submit-model")
# # TODO: add response_model = ... for data validation
# async def pv_calc(user_input: UserInputForm):
#     logger.info(
#         f"\nPOST:\t/dashboard/submit-model --> Received request: user_input={user_input}"
#     )

#     # Determine user_id
#     user_id = 123

#     # Process user input and write to database
#     model_id = await process_user_input(db_client, user_input, user_id)
#     if not model_id:
#         logger.error("Error processing user input")
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Error processing user input",
#         )

#     logger.info(f"\nPOST:\t/dashboard/submit-model --> Return Model ID: {model_id}")

#     return model_id


# @app.get("/dashboard/run-simulation")
# async def run_simulation(model_id: str):
#     logger.info(
#         f"\nGET:\t/dashboard/run-simulation --> Received request: model_id={model_id}"
#     )
#     # Fetch the model specifications
#     sim_model_specs = await db_client.find_one_by_id("model_specs", model_id)
#     sim_id = sim_model_specs["sim_id"]

#     # Start ferntree simulation
#     sim_run = await run_ferntree_simulation(sim_id, model_id)

#     if sim_run:
#         logger.info(
#             f"\nGET:\t/dashboard/run-simulation --> Sim {sim_id} ran successfully!"
#         )
#         return {"sim_run_success": True}
#     else:
#         logger.info(f"\n/dashboard/run-simulation --> Sim {sim_id} failed!")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error running simulation",
#         )


# @app.get("/dashboard/simulation-results")
# async def fetch_simulation_results(model_id: str):
#     logger.info(
#         f"\nGET:\t/dashboard/simulation-results --> Received request: model_id={model_id}"
#     )

#     # Fetch the model specifications TODO: stupid to do this again here!!!
#     sim_model_specs = await db_client.find_one_by_id("model_specs", model_id)
#     sim_model_specs_doc = ModelSpecsDoc(**sim_model_specs)
#     sim_id = sim_model_specs_doc.sim_id

#     # Evaluate simulation results
#     sim_eval_id, sim_evaluation = await evaluate_simulation_results(
#         db_client, sim_id, sim_model_specs_doc.sim_model_specs
#     )
#     if not sim_evaluation or not sim_eval_id:
#         logger.error(
#             f"Error evaluating simulation results. model_id={model_id}, sim_id={sim_id}, sim_eval_id={sim_eval_id}"
#         )
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Error evaluating simulation results",
#         )

#     logger.info(
#         f"\nGET:\t/dashboard/simulation-results --> Return Simulation Evaluation: {sim_evaluation.sim_id}"
#     )
#     return sim_evaluation


# @app.get("/dashboard/model-summary")
# async def fetch_model_summary(model_id: str):
#     logger.info(
#         f"\nGET:\t/dashboard/model-summary --> Received request: model_id={model_id}"
#     )

#     # Fetch the model specifications TODO: stupid to do this again here!!!
#     sim_model_specs = await db_client.find_one_by_id("model_specs", model_id)
#     sim_model_specs_doc = ModelSpecsDoc(**sim_model_specs)
#     model_summary = {
#         "location": sim_model_specs_doc.sim_model_specs.sim_params.location,
#         "electr_cons": sim_model_specs_doc.sim_model_specs.house.baseload.annual_consumption,
#         "roof_incl": sim_model_specs_doc.sim_model_specs.house.pv.roof_tilt,
#         "roof_azimuth": sim_model_specs_doc.sim_model_specs.house.pv.roof_azimuth,
#         "peak_power": sim_model_specs_doc.sim_model_specs.house.pv.peak_power,
#         "battery_cap": sim_model_specs_doc.sim_model_specs.house.battery.capacity,
#     }

#     logger.info(
#         f"\nGET:\t/dashboard/model-summary --> Return Model Summary: {model_summary}"
#     )
#     return model_summary


# @app.post("/dashboard/sim-timeseries-data")
# async def fetch_timeseries_data(request_body: TimeseriesDataRequest):
#     logger.info(
#         f"\nPOST:\t/dashboard/sim-timeseries-data --> Received request: {request_body}"
#     )

#     # Fetch the model specifications TODO: stupid to do this again here!!!
#     sim_model_specs = await db_client.find_one_by_id(
#         "model_specs", request_body.s_model_id
#     )
#     sim_id = sim_model_specs["sim_id"]

#     try:
#         start_date = datetime.fromisoformat(request_body.start_date).timestamp()
#         end_date = datetime.fromisoformat(request_body.end_date).timestamp()
#     except ValueError as e:
#         logger.error(f"Error parsing datetime: {e}")
#         raise HTTPException(status_code=400, detail="Invalid datetime format")

#     # Fetch the timeseries data of the simulation
#     timeseries_data = await db_client.fetch_timeseries_data(sim_id=sim_id)

#     # Filter the timeseries data to only include data within the given date range
#     filtered_timeseries_data = [
#         FilteredTimeseriesData(**data)
#         for data in timeseries_data
#         if start_date <= data["time"] <= end_date
#     ]

#     formatted_timeseries_data = format_timeseries_data(filtered_timeseries_data)

#     logger.info(
#         f"\nPOST:\t/dashboard/sim-timeseries-data --> Return timeseries data: {len(formatted_timeseries_data)} data points"
#     )

#     return formatted_timeseries_data  # TODO: define data model for response


# @app.get("/dashboard/pv-monthly-gen")
# async def fetch_pv_monthly_gen_data(model_id: str):
#     logger.info(
#         f"\nGET:\t/dashboard/pv-monthly-gen --> Received request: model_id={model_id}"
#     )
#     # Fetch the model specifications TODO: stupid to do this again here!!!
#     sim_model_specs = await db_client.find_one_by_id("model_specs", model_id)
#     sim_id = sim_model_specs["sim_id"]

#     # Fetch the timeseries data of the simulation
#     timeseries_data = await db_client.fetch_timeseries_data(sim_id=sim_id)

#     # Calculate the monthly PV generation data
#     monthly_pv_gen_data = await calc_monthly_pv_gen_data(timeseries_data)

#     logger.info(
#         f"\nGET:\t/dashboard/pv-monthly-gen --> Return Monthly PV Generation Data: {monthly_pv_gen_data}"
#     )
#     return monthly_pv_gen_data
