import logging
import os
from datetime import datetime
from logging import Logger
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from backend.database.models import (
    FinFormData,
    FinResults,
    ModelDataIn,
    ModelDataOut,
    SimDataIn,
    SimResultsEval,
    SimTimestep,
    SimTimestepOut,
    StartEndTimes,
)
from backend.database.mongodb import MongoClient
from backend.utils.auth_funcs import check_user_exists
from backend.utils.sim_funcs import (
    calc_fin_results,
    eval_sim_results,
    get_sim_input_data,
    run_ferntree_simulation,
)

# Set up logger
LOGGERNAME: str = "fastapi_logger"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger: Logger = logging.getLogger(LOGGERNAME)

# Create a FastAPI instance
app: FastAPI = FastAPI()

# Create a MongoDB client
db_client: MongoClient = MongoClient()

# Load config from .env file:
load_dotenv("./.env")
FRONTEND_BASE_URI: str = os.environ["FRONTEND_BASE_URI"]

# Configure CORS
origins: list[str] = FRONTEND_BASE_URI.split(",") + ["*"]

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
    """Submit a new model to the database.

    Args:
        user_id (str): The ID of the user submitting the model.
        model_data (ModelDataIn): The model data to be submitted.

    Returns:
        str: The ID of the newly created model.

    Raises:
        HTTPException: If there's an error inserting the model data into the database.

    """
    logger.info(
        f"\nPOST:\t/workspace/models/submit-model --> "
        f"Received request: user_id={user_id}, model_data={model_data}"
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
    """Fetch all models for a given user.

    Args:
        user_id (str): The ID of the user whose models are to be fetched.

    Returns:
        list[ModelDataOut]: A list of models associated with the user.

    """
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
    """Delete a specific model.

    Args:
        user_id (str): The ID of the user requesting the deletion.
        model_id (str): The ID of the model to be deleted.

    Returns:
        str: The ID of the deleted model.

    Raises:
        HTTPException: If the model with the given ID is not found.

    """
    logger.info(
        f"DELETE:\t/workspace/models/delete-model --> "
        f"Received request: user_id={user_id}, model_id={model_id}"
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
    """Run a simulation for a specific model.

    Args:
        user_id (str): The ID of the user requesting the simulation.
        model_id (str): The ID of the model to simulate.

    Returns:
        dict[str, bool]: A dictionary indicating whether simulation run was successful.

    Raises:
        HTTPException: If there's an error updating the sim ID or running the sim.

    """
    logger.info(
        f"GET:\t/workspace/simulations/run-sim --> "
        f"Received request: user_id={user_id}, model_id={model_id}"
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
            f"GET:\t/workspace/simulations/run-simulation --> "
            f"Sim {sim_id} ran successfully!"
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
    """Fetch simulation results for a specific model.

    Args:
        user_id (str): The ID of the user requesting the results.
        model_id (str): The ID of the model for which to fetch results.

    Returns:
        SimResultsEval: The evaluated simulation results.

    """
    logger.info(
        f"GET:\t/workspace/simulations/fetch-sim-results --> "
        f"Received request: user_id={user_id}, model_id={model_id}"
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
            f"GET:\t/workspace/simulations/fetch-sim-results --> "
            f"Evaluating sim results for model_id={model_id}"
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
    """Fetch simulation timeseries data for a specific model within a given time range.

    Args:
        user_id (str): The ID of the user requesting the data.
        model_id (str): The ID of the model for which to fetch timeseries data.
        request_body (StartEndTimes): The start and end times for the requested data.

    Returns:
        list[SimTimestepOut]: A list of sim timesteps within the specified time range.

    Raises:
        HTTPException: If there's an error parsing the datetime or fetching the data.

    """
    logger.info(
        f"POST:\t/workspace/simulations/fetch-sim-timeseries --> "
        f"Received request: user={user_id}, model={model_id}, request={request_body}"
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
            StateOfCharge=timestep.Soc_bat / battery_cap * 100
            if battery_cap > 0
            else 0,  # in %
        )
        for timestep in sim_results
        if start_time <= timestep.time <= end_time
    ]

    if len(sim_timeseries_data) > 20 * 24:
        sim_timeseries_data = sim_timeseries_data[: 20 * 24]
        logger.info(
            "POST:\t/workspace/simulations/fetch-sim-timeseries --> "
            "Fetch too large, returning only 20 days of data"
        )
    logger.info(
        f"POST:\t/workspace/simulations/fetch-sim-timeseries --> "
        f"Return timeseries data: {len(sim_timeseries_data)} data points"
    )

    return sim_timeseries_data


@app.post("/workspace/finances/submit-fin-form-data", response_model=str)
@check_user_exists(db_client)
async def submit_fin_form_data(user_id: str, fin_form_data_sub: FinFormData) -> str:
    """Submit financial form data for a model and calculate fin results if necessary.

    Args:
        user_id (str): The ID of the user submitting the data.
        fin_form_data_sub (FinFormData): The financial form data to be submitted.

    Returns:
        str: The ID of the model for which financial data was submitted.

    """
    logger.info(
        f"\nPOST:\t/workspace/finances/submit-fin-form-data --> "
        f"Received request: user_id={user_id}"
    )

    # Fetch fin form data from database
    model_id: str = fin_form_data_sub.model_id
    doc: Optional[dict[str, Any]] = await db_client.fetch_document("finances", model_id)
    fin_form_data_db: Optional[FinFormData] = FinFormData(**doc) if doc else None

    # If model has no form data (1:1 relation),
    # then write form data to database and calculate financial results
    # If model has form data, then check if form data has changed and if so,
    # write new form data to database and calculate financial results
    # Else nothing to do because finances have already been calculated for this formdata
    if (fin_form_data_db is None) or (fin_form_data_sub != fin_form_data_db):
        logger.info(
            f"POST:\t/workspace/finances/submit-fin-form-data --> "
            f"Calculating financial results for model {model_id}"
        )
        # Write fin form data to database
        await db_client.insert_document("finances", fin_form_data_sub)
        # Calculate financial results
        fin_results: FinResults = await calc_fin_results(db_client, fin_form_data_sub)
        await db_client.insert_document("fin_results", fin_results)
    else:
        logger.info(
            f"POST:\t/workspace/finances/submit-fin-form-data --> "
            f"Financial results already calculated for model {model_id}"
        )

    logger.info(
        f"POST:\t/workspace/finances/submit-fin-form-data --> "
        f"Financial results ready for model {model_id}"
    )

    return model_id


@app.get("/workspace/finances/fetch-fin-results", response_model=FinResults)
@check_user_exists(db_client)
async def fetch_fin_results(user_id: str, model_id: str) -> FinResults:
    """Fetch financial results for a specific model.

    Args:
        user_id (str): The ID of the user requesting the results.
        model_id (str): The ID of the model for which to fetch financial results.

    Returns:
        FinResults: The financial results for the specified model.

    Raises:
        RuntimeError: If fetching the financial results fails.

    """
    logger.info(
        f"GET:\t/workspace/finances/fetch-fin-results --> "
        f"Received request: user_id={user_id}, model_id={model_id}"
    )

    # Fetch financial results from database
    doc: Optional[dict[str, Any]] = await db_client.fetch_document(
        "fin_results", model_id
    )
    if doc is None:
        raise RuntimeError(f"Failed to fetch financial results for model_id {model_id}")
    fin_results: FinResults = FinResults(**doc)

    logger.info(
        f"GET:\t/workspace/finances/fetch-fin-results --> "
        f"Return financial results for model {model_id}"
    )

    return fin_results


@app.get("/workspace/finances/fetch-fin-form-data", response_model=list[FinFormData])
@check_user_exists(db_client)
async def fetch_fin_form_data(user_id: str) -> list[FinFormData]:
    """Fetch financial form data for all models of a user.

    Args:
        user_id (str): The ID of the user requesting the data.

    Returns:
        list[FinFormData]: A list of financial form data for all models of the user.

    """
    logger.info(
        f"GET:\t/workspace/finances/fetch-fin-form-data --> "
        f"Received request: user_id={user_id}"
    )

    # Fetch all models of the user
    models: list[ModelDataOut] = await db_client.fetch_models(user_id)

    # Fetch fin form data for all models (if available) from database
    fin_form_data_all: list[FinFormData] = []
    for model in models:
        model_id = model.model_id
        doc: Optional[dict[str, Any]] = await db_client.fetch_document(
            "finances", model_id
        )
        if doc:
            fin_form_data: FinFormData = FinFormData(**doc)
            fin_form_data_all.append(fin_form_data)

    logger.info(
        f"GET:\t/workspace/finances/fetch-fin-form-data --> "
        f"Return fin form data for {len(fin_form_data_all)} models"
    )

    return fin_form_data_all
