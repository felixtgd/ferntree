import asyncio

from src.domains.ferntree.main import build_and_run_simulation


async def run_simulation(sim_id: str, model_id: str) -> None:
    """Run the synchronous simulation without blocking the event loop."""
    await asyncio.to_thread(build_and_run_simulation, sim_id=sim_id, model_id=model_id)
