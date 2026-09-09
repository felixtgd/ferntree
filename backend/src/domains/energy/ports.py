from typing import Optional, Protocol


class TimestepReader(Protocol):
    """Read-side persistence interface required by energy evaluation."""

    async def fetch_timesteps(
        self,
        model_id: str,
        user_id: int,
        start: Optional[float] = None,
        end: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list[dict[str, float]]:
        """Fetch simulation timesteps for a model and user.

        Args:
            model_id (str): String identifier of the model.
            user_id (int): Identifier of the model owner.
            start (Optional[float]): Inclusive start timestamp.
            end (Optional[float]): Inclusive end timestamp.
            limit (Optional[int]): Maximum number of rows to return.

        Returns:
            list[dict[str, float]]: Simulation timestep records.

        """
        ...
