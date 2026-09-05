from logging import Logger
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import check_user_exists, get_db_client, get_logger
from src.database.models import (
    ModelDataIn,
    ModelDataOut,
)
from src.database.postgres import Database

PREFIX: str = "/workspace/models"
TAG: str = "models"

router: APIRouter = APIRouter(
    prefix=PREFIX,
    tags=[TAG],
    dependencies=[Depends(check_user_exists)],
)


@router.post("/submit-model", response_model=str)
async def submit_model(
    user_id: str,
    model_data: ModelDataIn,
    db_client: Database = Depends(get_db_client),
    logger: Logger = Depends(get_logger),
) -> str:
    """Submit a new model to the database.

    Args:
        user_id (str): The ID of the user submitting the model.
        model_data (ModelDataIn): The model data to be submitted.
        db_client (Database): The database client instance.
        logger (Logger): The logger instance.

    Returns:
        str: The ID of the newly created model.

    Raises:
        HTTPException: If there's an error inserting the model data into the database.

    """
    logger.info(
        f"\nPOST:\t{PREFIX}/submit-model --> "
        f"Received request: user_id={user_id}, model_data={model_data}"
    )

    # Insert model data into database
    model_id: Optional[str] = await db_client.insert_model(model_data.model_dump())
    if model_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error inserting model data into database.",
        )

    logger.info(f"POST:\t{PREFIX}/submit-model --> Return Model ID: {model_id}")

    return model_id


@router.get("/fetch-models", response_model=list[ModelDataOut])
async def fetch_models(
    user_id: str,
    db_client: Database = Depends(get_db_client),
    logger: Logger = Depends(get_logger),
) -> list[ModelDataOut]:
    """Fetch all models for a given user.

    Args:
        user_id (str): The ID of the user whose models are to be fetched.
        db_client (Database): The database client instance.
        logger (Logger): The logger instance.

    Returns:
        list[ModelDataOut]: A list of models associated with the user.

    """
    logger.info(f"GET:\t{PREFIX}/fetch-models --> Received request: user_id={user_id}")

    # Fetch all models of the user
    models: list[ModelDataOut] = await db_client.fetch_models(user_id)

    logger.info(f"GET:\t{PREFIX}/fetch-models --> Return {len(models)} models")

    return models


@router.delete("/delete-model", response_model=str)
async def delete_model(
    user_id: str,
    model_id: str,
    db_client: Database = Depends(get_db_client),
    logger: Logger = Depends(get_logger),
) -> str:
    """Delete a specific model.

    Args:
        user_id (str): The ID of the user requesting the deletion.
        model_id (str): The ID of the model to be deleted.
        db_client (Database): The database client instance.
        logger (Logger): The logger instance.

    Returns:
        str: The ID of the deleted model.

    Raises:
        HTTPException: If the model with the given ID is not found.

    """
    logger.info(
        f"DELETE:\t{PREFIX}/delete-model --> "
        f"Received request: user_id={user_id}, model_id={model_id}"
    )

    # Delete the model
    delete_result_acknowledged: bool = await db_client.delete_model(model_id, user_id)
    if not delete_result_acknowledged:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with ID {model_id} not found.",
        )

    logger.info(f"DELETE:\t{PREFIX}/delete-model --> Deleted model with ID: {model_id}")

    return model_id
