from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    """Represents a user in the system.

    Attributes:
        user_id (int): The unique identifier for the user.
        name (str): The user's name.
        email (str): The user's email address.
        image (str): URL or path to the user's profile image.
        emailVerified (Optional[str]): Timestamp of when the email was verified,
                                        if applicable.

    """

    user_id: int
    name: str
    email: str
    image: str
    emailVerified: Optional[str]


class StartEndTimes(BaseModel):
    """Represents start and end times for a time range.

    Attributes:
        start_time (str): The start time of the range.
        end_time (str): The end time of the range.

    """

    start_time: str
    end_time: str
