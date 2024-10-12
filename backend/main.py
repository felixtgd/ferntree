import os
import logging
from logging import Logger
from typing import Optional, Any
from dotenv import load_dotenv

from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from backend.database.models import (
    ModelDataIn,
    ModelDataOut,
    SimDataIn,
    SimResultsEval,
    StartEndTimes,
    SimTimestep,
    SimTimestepOut,
    FinFormData,
    FinResults,
)
from backend.database.mongodb import MongoClient
from backend.utils.sim_funcs import (
    get_sim_input_data,
    run_ferntree_simulation,
    eval_sim_results,
    calc_fin_results,
)

from backend.utils.auth_funcs import check_user_exists


# Set up logger
LOGGERNAME: str = "fastapi_logger"
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger: Logger = logging.getLogger(LOGGERNAME)

# Create a FastAPI instance
app: FastAPI = FastAPI()

# Create a MongoDB client
db_client: MongoClient = MongoClient()

# Load config from .env file:
load_dotenv("./.env")
FRONTEND_BASE_URI: str = os.environ["FRONTEND_BASE_URI"]

# Configure CORS
origins: list[str] = [
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
async def submit_model(user_id: str, model_data: ModelDataIn) -> str:
    logger.info(
        f"\nPOST:\t/workspace/models/submit-model --> Received request: user_id={user_id}, model_data={model_data}"
    )

    # Insert model data into database
    model_id: Optional[str] = await db_client.insert_model(model_data.model_dump())
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
async def fetch_models(user_id: str) -> list[ModelDataOut]:
    logger.info(
        f"GET:\t/workspace/models/fetch-models --> Received request: user_id={user_id}"
    )

    # Fetch all models of the user
    models: list[ModelDataOut] = await db_client.fetch_models(user_id)

    logger.info(f"GET:\t/workspace/models/fetch-models --> Return {len(models)} models")

    return models


@app.delete("/workspace/models/delete-model", response_model=str)
@check_user_exists(db_client)
async def delete_model(user_id: str, model_id: str) -> str:
    logger.info(
        f"DELETE:\t/workspace/models/delete-model --> Received request: user_id={user_id}, model_id={model_id}"
    )

    # Delete the model
    delete_result_acknowledged: bool = await db_client.delete_model(model_id)
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
async def run_simulation(user_id: str, model_id: str) -> dict[str, bool]:
    logger.info(
        f"GET:\t/workspace/simulations/run-sim --> Received request: user_id={user_id}, model_id={model_id}"
    )

    # Fetch model data from database
    model_data: ModelDataOut = await db_client.fetch_model_by_id(model_id)

    # Get simulation input data
    sim_input_data: SimDataIn = await get_sim_input_data(model_data)

    # Insert simulation input data into database
    sim_id: str = await db_client.insert_document("simulations", sim_input_data)

    # Run the simulation
    sim_run: bool = await run_ferntree_simulation(model_id, sim_id)

    # If sim run was successful, insert sim_id into model doc in database
    if sim_run:
        sim_id_updated: bool = await db_client.update_sim_id_of_model(model_id, sim_id)
        if not sim_id_updated:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error updating sim_id {sim_id} of model {model_id}.",
            )
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
async def fetch_sim_results(user_id: str, model_id: str) -> SimResultsEval:
    logger.info(
        f"GET:\t/workspace/simulations/fetch-sim-results --> Received request: user_id={user_id}, model_id={model_id}"
    )

    # Check if sim results are already evaluated
    doc: Optional[dict[str, Any]] = await db_client.fetch_document(
        "sim_results_eval", model_id
    )
    sim_results_eval_existing: Optional[SimResultsEval] = (
        SimResultsEval(**doc) if doc else None
    )

    # If not, evaluate sim results
    if sim_results_eval_existing is None:
        logger.info(
            f"GET:\t/workspace/simulations/fetch-sim-results --> Evaluating sim results for model_id={model_id}"
        )
        sim_results_eval_new: SimResultsEval = await eval_sim_results(
            db_client, model_id
        )
        await db_client.insert_document("sim_results_eval", sim_results_eval_new)
        return sim_results_eval_new
    else:
        return sim_results_eval_existing


@app.post(
    "/workspace/simulations/fetch-sim-timeseries", response_model=list[SimTimestepOut]
)
@check_user_exists(db_client)
async def fetch_sim_timeseries(
    user_id: str, model_id: str, request_body: StartEndTimes
) -> list[SimTimestepOut]:
    logger.info(
        f"POST:\t/workspace/simulations/fetch-sim-timeseries --> Received request: user_id={user_id}, model_id={model_id}, requets body={request_body}"
    )

    try:
        start_time: float = datetime.fromisoformat(request_body.start_time).timestamp()
        end_time: float = datetime.fromisoformat(request_body.end_time).timestamp()
    except ValueError as e:
        logger.error(f"Error parsing datetime: {e}")
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    # Fetch sim results timeseries data
    doc: Optional[dict[str, Any]] = await db_client.fetch_document(
        "sim_results_ts", model_id
    )
    if doc is None:
        raise RuntimeError(
            f"Failed to fetch sim results timeseries for model_id {model_id}"
        )
    sim_results: list[SimTimestep] = [
        SimTimestep(**timestep) for timestep in doc["timeseries"]
    ]

    # Fetch model data
    model_data: ModelDataOut = await db_client.fetch_model_by_id(model_id)
    battery_cap: float = model_data.battery_cap

    # Filter the timeseries data to only include data within the given date range
    sim_timeseries_data: list[SimTimestepOut] = [
        SimTimestepOut(
            time=datetime.fromtimestamp(timestep.time).strftime("%d-%m-%Y %H:%M"),
            Load=timestep.P_base,
            PV=timestep.P_pv,
            Battery=timestep.P_bat,
            Total=timestep.P_base + timestep.P_pv + timestep.P_bat,
            StateOfCharge=timestep.Soc_bat / battery_cap * 100,  # in %
        )
        for timestep in sim_results
        if start_time <= timestep.time <= end_time
    ]

    logger.info(
        f"POST:\t/workspace/simulations/fetch-sim-timeseries --> Return timeseries data: {len(sim_timeseries_data)} data points"
    )

    return sim_timeseries_data


@app.post("/workspace/finances/submit-fin-form-data", response_model=str)
@check_user_exists(db_client)
async def submit_fin_form_data(user_id: str, fin_form_data_sub: FinFormData) -> str:
    logger.info(
        f"\nPOST:\t/workspace/finances/submit-fin-form-data --> Received request: user_id={user_id}"
    )

    # Fetch fin form data from database
    model_id: str = fin_form_data_sub.model_id
    doc: Optional[dict[str, Any]] = await db_client.fetch_document("finances", model_id)
    fin_form_data_db: Optional[FinFormData] = FinFormData(**doc) if doc else None

    # If model has no form data (1:1 relation),
    # then write form data to database and calculate financial results
    # If model has form data, then check if form data has changed and if so,
    # write new form data to database and calculate financial results
    # Else nothing to do because finances have already been calculated for this form data
    if (fin_form_data_db is None) or (fin_form_data_sub != fin_form_data_db):
        logger.info(
            f"POST:\t/workspace/finances/submit-fin-form-data --> Calculating financial results for model {model_id}"
        )
        # Write fin form data to database
        await db_client.insert_document("finances", fin_form_data_sub)
        # Calculate financial results
        fin_results: FinResults = await calc_fin_results(db_client, fin_form_data_sub)
        await db_client.insert_document("fin_results", fin_results)
    else:
        logger.info(
            f"POST:\t/workspace/finances/submit-fin-form-data --> Financial results already calculated for model {model_id}"
        )

    logger.info(
        f"POST:\t/workspace/finances/submit-fin-form-data --> Financial results ready for model {model_id}"
    )

    return model_id


@app.get("/workspace/finances/fetch-fin-results", response_model=FinResults)
@check_user_exists(db_client)
async def fetch_fin_results(user_id: str, model_id: str) -> FinResults:
    logger.info(
        f"GET:\t/workspace/finances/fetch-fin-results --> Received request: user_id={user_id}, model_id={model_id}"
    )

    # Fetch financial results from database
    doc: Optional[dict[str, Any]] = await db_client.fetch_document(
        "fin_results", model_id
    )
    if doc is None:
        raise RuntimeError(f"Failed to fetch financial results for model_id {model_id}")
    fin_results: FinResults = FinResults(**doc)

    logger.info(
        f"GET:\t/workspace/finances/fetch-fin-results --> Return financial results for model {model_id}"
    )

    return fin_results
