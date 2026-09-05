from logging import Logger

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import check_user_exists, get_db_client, get_logger
from src.database.models import (
    FinFormData,
    FinResults,
)
from src.database.postgres import Database
from src.utils.sim_funcs import (
    calc_fin_results,
)

PREFIX: str = "/workspace/finances"
TAG: str = "finances"

router: APIRouter = APIRouter(
    prefix=PREFIX,
    tags=[TAG],
    dependencies=[Depends(check_user_exists)],
)


@router.post("/submit-fin-form-data", response_model=str)
async def submit_fin_form_data(
    user_id: str,
    fin_form_data_sub: FinFormData,
    db_client: Database = Depends(get_db_client),
    logger: Logger = Depends(get_logger),
) -> str:
    """Submit financial form data for a model and calculate fin results if necessary.

    Args:
        user_id (str): The ID of the user submitting the data.
        fin_form_data_sub (FinFormData): The financial form data to be submitted.
        db_client (Database): The database client instance.
        logger (Logger): The logger instance.

    Returns:
        str: The ID of the model for which financial data was submitted.

    """
    logger.info(
        f"\nPOST:\t{PREFIX}/submit-fin-form-data --> "
        f"Received request: user_id={user_id}"
    )

    # Fetch fin form data from database
    model_id: str = fin_form_data_sub.model_id
    fin_form_data_db = await db_client.fetch_finances(model_id, user_id)

    # If model has no form data (1:1 relation),
    # then write form data to database and calculate financial results
    # If model has form data, then check if form data has changed and if so,
    # write new form data to database and calculate financial results
    # Else nothing to do because finances have already been calculated for this formdata
    if (fin_form_data_db is None) or (fin_form_data_sub != fin_form_data_db):
        logger.info(
            f"POST:\t{PREFIX}/submit-fin-form-data --> "
            f"Calculating financial results for model {model_id}"
        )
        # Write fin form data to database
        await db_client.upsert_finances(fin_form_data_sub, user_id)
        # Calculate financial results
        fin_results: FinResults = await calc_fin_results(
            db_client, fin_form_data_sub, user_id
        )
        await db_client.upsert_fin_results(fin_results, user_id)
    else:
        logger.info(
            f"POST:\t{PREFIX}/submit-fin-form-data --> "
            f"Financial results already calculated for model {model_id}"
        )

    logger.info(
        f"POST:\t{PREFIX}/submit-fin-form-data --> "
        f"Financial results ready for model {model_id}"
    )

    return model_id


@router.get("/fetch-fin-results", response_model=FinResults)
async def fetch_fin_results(
    user_id: str,
    model_id: str,
    db_client: Database = Depends(get_db_client),
    logger: Logger = Depends(get_logger),
) -> FinResults:
    """Fetch financial results for a specific model.

    Args:
        user_id (str): The ID of the user requesting the results.
        model_id (str): The ID of the model for which to fetch financial results.
        db_client (Database): The database client dependency.
        logger (Logger): The logger dependency.

    Returns:
        FinResults: The financial results for the specified model.

    Raises:
        HTTPException: If financial results are not available for the model.

    """
    logger.info(
        f"GET:\t{PREFIX}/fetch-fin-results --> "
        f"Received request: user_id={user_id}, model_id={model_id}"
    )

    # Fetch financial results from database
    fin_results = await db_client.fetch_fin_results(model_id, user_id)
    if fin_results is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Financial results for model {model_id} not found.",
        )

    logger.info(
        f"GET:\t{PREFIX}/fetch-fin-results --> "
        f"Return financial results for model {model_id}"
    )

    return fin_results


@router.get("/fetch-fin-form-data", response_model=list[FinFormData])
async def fetch_fin_form_data(
    user_id: str,
    db_client: Database = Depends(get_db_client),
    logger: Logger = Depends(get_logger),
) -> list[FinFormData]:
    """Fetch financial form data for all models of a user.

    Args:
        user_id (str): The ID of the user requesting the data.
        db_client (Database): The database client dependency.
        logger (Logger): The logger dependency.

    Returns:
        list[FinFormData]: A list of financial form data for all models of the user.

    """
    logger.info(
        f"GET:\t{PREFIX}/fetch-fin-form-data --> Received request: user_id={user_id}"
    )

    # Fetch fin form data for all models (if available) in one query
    fin_form_data_all = await db_client.fetch_finances_for_user(user_id)

    logger.info(
        f"GET:\t{PREFIX}/fetch-fin-form-data --> "
        f"Return fin form data for {len(fin_form_data_all)} models"
    )

    return fin_form_data_all
