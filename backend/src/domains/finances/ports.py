from typing import Optional, Protocol

from src.db.schemas import ModelDataOut, SimResultsEval


class FinanceDataReader(Protocol):
    """Read-side persistence interface required by financial calculation."""

    async def fetch_model_by_id(self, model_id: str, user_id: int) -> ModelDataOut:
        """Fetch model data for a model and user.

        Args:
            model_id (str): String identifier of the model.
            user_id (int): Identifier of the model owner.

        Returns:
            ModelDataOut: The requested model data.

        """
        ...

    async def fetch_sim_results_eval(
        self, model_id: str, user_id: int
    ) -> Optional[SimResultsEval]:
        """Fetch evaluated simulation results for a model and user.

        Args:
            model_id (str): String identifier of the model.
            user_id (int): Identifier of the model owner.

        Returns:
            SimResultsEval | None: Evaluation results, if available.

        """
        ...
