from datetime import datetime
from logging import Logger

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import check_user_exists, get_db_client, get_logger
from src.database.models import (
    ModelDataOut,
    SimDataIn,
    SimResultsEval,
    SimTimestep,
    SimTimestepOut,
    StartEndTimes,
)
from src.database.postgres import Database
from src.utils.sim_funcs import (
    eval_sim_results,
    get_sim_input_data,
    run_ferntree_simulation,
)

PREFIX: str = "/workspace/simulations"
TAG: str = "simulations"

router: APIRouter = APIRouter(
    prefix=PREFIX,
    tags=[TAG],
    dependencies=[Depends(check_user_exists)],
)


@router.get("/run-sim", response_model=dict[str, bool])
async def run_simulation(
    user_id: str,
    model_id: str,
    db_client: Database = Depends(get_db_client),
    logger: Logger = Depends(get_logger),
) -> dict[str, bool]:
    """Run a simulation for a specific model.

    Args:
        user_id (str): The ID of the user requesting the simulation.
        model_id (str): The ID of the model to simulate.
        db_client (Database): The database client instance.
        logger (Logger): The logger instance.

    Returns:
        dict[str, bool]: A dictionary indicating whether simulation run was successful.

    Raises:
        HTTPException: If there's an error updating the sim ID or running the sim.

    """
    logger.info(
        f"GET:\t{PREFIX}/run-sim --> "
        f"Received request: user_id={user_id}, model_id={model_id}"
    )

    # Fetch model data from database
    try:
        model_data: ModelDataOut = await db_client.fetch_model_by_id(model_id, user_id)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with ID {model_id} not found.",
        )

    # Get simulation input data
    sim_input_data: SimDataIn = await get_sim_input_data(model_data)

    # Insert simulation input data into database
    sim_id: str = await db_client.upsert_simulation(sim_input_data, user_id)

    # Run the simulation
    sim_run: bool = await run_ferntree_simulation(model_id, sim_id)

    # If sim run was successful, insert sim_id into model doc in database
    if sim_run:
        sim_id_updated: bool = await db_client.update_sim_id_of_model(
            model_id, sim_id, user_id
        )
        if not sim_id_updated:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error updating sim_id {sim_id} of model {model_id}.",
            )
        logger.info(f"GET:\t{PREFIX}/run-simulation --> Sim {sim_id} ran successfully!")
        return {"run_successful": True}
    else:
        logger.info(
            f"ERROR:\t/workspace/simulations/run-simulation --> Sim {sim_id} failed!"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error running simulation",
        )


@router.get("/fetch-sim-results", response_model=SimResultsEval)
async def fetch_sim_results(
    user_id: str,
    model_id: str,
    db_client: Database = Depends(get_db_client),
    logger: Logger = Depends(get_logger),
) -> SimResultsEval:
    """Fetch simulation results for a specific model.

    Args:
        user_id (str): The ID of the user requesting the results.
        model_id (str): The ID of the model for which to fetch results.
        db_client (Database): The database client for fetching simulation results.
        logger (Logger): The logger for logging information and errors.

    Returns:
        SimResultsEval: The evaluated simulation results.

    """
    logger.info(
        f"GET:\t{PREFIX}/fetch-sim-results --> "
        f"Received request: user_id={user_id}, model_id={model_id}"
    )

    # Check if sim results are already evaluated
    sim_results_eval_existing = await db_client.fetch_sim_results_eval(
        model_id, user_id
    )

    # If not, evaluate sim results
    if sim_results_eval_existing is None:
        logger.info(
            f"GET:\t{PREFIX}/fetch-sim-results --> "
            f"Evaluating sim results for model_id={model_id}"
        )
        sim_results_eval_new: SimResultsEval = await eval_sim_results(
            db_client, model_id, user_id
        )
        await db_client.upsert_sim_results_eval(sim_results_eval_new, user_id)
        return sim_results_eval_new
    else:
        return sim_results_eval_existing


@router.post("/fetch-sim-timeseries", response_model=list[SimTimestepOut])
async def fetch_sim_timeseries(
    user_id: str,
    model_id: str,
    request_body: StartEndTimes,
    db_client: Database = Depends(get_db_client),
    logger: Logger = Depends(get_logger),
) -> list[SimTimestepOut]:
    """Fetch simulation timeseries data for a specific model within a given time range.

    Args:
        user_id (str): The ID of the user requesting the data.
        model_id (str): The ID of the model for which to fetch timeseries data.
        request_body (StartEndTimes): The start and end times for the requested data.
        db_client (Database): The database client for fetching simulation data.
        logger (Logger): The logger for logging information and errors.

    Returns:
        list[SimTimestepOut]: A list of sim timesteps within the specified time range.

    Raises:
        HTTPException: If there's an error parsing the datetime or fetching the data.

    """
    logger.info(
        f"POST:\t{PREFIX}/fetch-sim-timeseries --> "
        f"Received request: user={user_id}, model={model_id}, request={request_body}"
    )

    try:
        start_time: float = datetime.fromisoformat(request_body.start_time).timestamp()
        end_time: float = datetime.fromisoformat(request_body.end_time).timestamp()
    except ValueError as e:
        logger.error(f"Error parsing datetime: {e}")
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    sim_results = await db_client.fetch_timesteps(
        model_id, user_id, start_time, end_time, 20 * 24
    )

    # Fetch model data
    try:
        model_data: ModelDataOut = await db_client.fetch_model_by_id(model_id, user_id)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with ID {model_id} not found.",
        )
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
        for timestep in (SimTimestep(**item) for item in sim_results)
    ]

    if len(sim_timeseries_data) > 20 * 24:
        sim_timeseries_data = sim_timeseries_data[: 20 * 24]
        logger.info(
            f"POST:\t{PREFIX}/fetch-sim-timeseries --> "
            "Fetch too large, returning only 20 days of data"
        )
    logger.info(
        f"POST:\t{PREFIX}/fetch-sim-timeseries --> "
        f"Return timeseries data: {len(sim_timeseries_data)} data points"
    )

    return sim_timeseries_data
