from typing import Optional, Protocol


class TimestepReader(Protocol):
    """Read-side persistence interface required by energy evaluation."""

    async def fetch_timesteps(
        self,
        model_id: str,
        user_id: str,
        start: Optional[float] = None,
        end: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list[dict[str, float]]:
        """Fetch simulation timesteps for a model and user."""
        ...
