"""Expose the asynchronous database repositories through one client."""

from src.db.async_client.repositories.finance_repo import FinanceRepository
from src.db.async_client.repositories.models_repo import ModelsRepository
from src.db.async_client.repositories.simulation_repo import (
    SimulationRepository,
)


class DatabaseClient(ModelsRepository, SimulationRepository, FinanceRepository):
    """Unified DB client exposing all repository methods."""

    pass
