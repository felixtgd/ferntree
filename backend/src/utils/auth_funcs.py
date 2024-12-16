from functools import wraps
from typing import Any, Awaitable, Callable, Optional, TypeVar

from fastapi import HTTPException, status

from src.database.mongodb import MongoClient

# Define a type variable for the function
F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def check_user_exists(db_client: MongoClient) -> Callable[[F], F]:
    """A decorator that checks if a user exists in the database before
    executing the decorated function.

    This decorator is designed to be used with FastAPI route handlers.
    It expects the decorated function to have a 'user_id' parameter, either as a
    keyword argument or as part of a Pydantic model passed to the function.

    Args:
        db_client (MongoClient): An instance of the MongoDB client used to
                                    check user existence.

    Returns:
        Callable[[F], F]: A decorator function that wraps the original function.

    Raises:
        HTTPException:
            - 400 Bad Request if the user_id is not provided in the function arguments.
            - 404 Not Found if the user with the given ID does not exist in the database

    Usage:
        @app.get("/some-route")
        @check_user_exists(db_client)
        async def some_route_handler(user_id: str):
            # Function implementation

    Note:
        - The decorated function must be an async function.
        - The 'user_id' parameter is expected to be a string.
        - This decorator adds overhead to each request as it performs a database check.
          Consider caching or other optimization techniques for high-traffic scenarios.

    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            user_id: Optional[str] = kwargs.get("user_id")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User ID is required.",
                )

            user_exists: bool = await db_client.check_user_exists(user_id)
            if not user_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found.",
                )

            return await func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
