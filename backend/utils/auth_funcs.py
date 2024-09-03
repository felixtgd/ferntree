from functools import wraps
from fastapi import HTTPException, status

from backend.database.mongodb import MongoClient


def check_user_exists(db_client: MongoClient):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id: str = kwargs.get("user_id")

            if not user_id:
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

        return wrapper

    return decorator
