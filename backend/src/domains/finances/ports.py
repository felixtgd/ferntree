from typing import Optional, Protocol

from src.db.schemas import ModelDataOut, SimResultsEval


class FinanceDataReader(Protocol):
    """Read-side persistence interface required by financial calculation."""

    async def fetch_model_by_id(self, model_id: str, user_id: str) -> ModelDataOut:
        """Fetch model data for a model and user."""
        ...

    async def fetch_sim_results_eval(
        self, model_id: str, user_id: str
    ) -> Optional[SimResultsEval]:
        """Fetch evaluated simulation results for a model and user."""
        ...
