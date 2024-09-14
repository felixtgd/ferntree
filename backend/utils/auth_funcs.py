from functools import wraps
from fastapi import HTTPException, status
from typing import Any, Callable, TypeVar, Awaitable, Optional

from backend.database.mongodb import MongoClient

# Define a type variable for the function
F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def check_user_exists(db_client: MongoClient) -> Callable[[F], F]:
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
