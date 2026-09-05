from src.db.repositories.finance_repo import FinanceRepository
from src.db.repositories.models_repo import ModelsRepository
from src.db.repositories.simulation_repo import SimulationRepository


class DatabaseClient(ModelsRepository, SimulationRepository, FinanceRepository):
    """Unified DB client exposing all repository methods."""

    pass
