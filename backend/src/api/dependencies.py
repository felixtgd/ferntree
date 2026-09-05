import logging
from logging import Logger

from fastapi import Depends, HTTPException, status

from src.database.postgres import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

db_client: Database = Database()


def get_logger(name: str = "fastapi_logger") -> Logger:
    """Get a configured logger instance.

    Args:
        name (str): The name of the logger. Defaults to "fastapi_logger".

    Returns:
        Logger: Configured logger instance.

    """
    return logging.getLogger(name)


def get_db_client() -> Database:
    """Get the API database client.

    Returns:
        Database: The API database client instance.

    """
    return db_client


async def check_user_exists(user_id: str, db_client: Database = Depends(get_db_client)):
    """Dependency to check if a user exists in the database.

    Args:
        user_id (str): The ID of the user to check.
        db_client (Database): The database client instance.

    Returns:
        bool: True if the user exists, otherwise an HTTPException is raised.

    Raises:
        HTTPException: If the user does not exist.

    """
    user_exists: bool = await db_client.check_user_exists(user_id)
    if user_exists:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
