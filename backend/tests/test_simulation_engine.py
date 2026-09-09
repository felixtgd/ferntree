from typing import Any

import pytest

from src.db.schemas import SimTimestep
from src.domains.ferntree import sim_builder
from src.domains.ferntree.main import build_and_run_simulation

TIMEBASE = 3600
TIMESTEPS = 365 * 24 * 3600 // TIMEBASE
SIMULATION_CONFIG: dict[str, Any] = {
    "timebase": TIMEBASE,
    "timezone": "Europe/Berlin",
    "T_amb": [15.0] * TIMESTEPS,
    "G_i": [200.0] * TIMESTEPS,
    "baseload_annual_consumption": 3500.0,
    "pv_roof_tilt": 30,
    "pv_roof_azimuth": 0,
    "pv_peak_power": 5.0,
    "battery_capacity": 5.0,
    "battery_max_power": 5.0,
    "battery_soc_init": 0.5,
    "batctrl_planning_horizon": 1,
    "batctrl_useable_capacity": 0.8,
    "batctrl_greedy": True,
    "batctrl_opt_fill": False,
}


class FakeDbClient:
    """Provide fixed simulation input and capture validated timestep results."""

    def __init__(self) -> None:
        """Initialize the captured load profile and results."""
        self.load_profile: list[float] = []
        self.results: list[SimTimestep] = []

    def load_config(self) -> dict[str, Any]:
        """Return the fixed configuration for this simulation run."""
        return SIMULATION_CONFIG

    def ensure_load_profile(
        self, profile_id: int, profile_type: str, load_profile: list[float]
    ) -> None:
        """Store the generated load profile for the builder to retrieve."""
        self.load_profile = load_profile

    def get_load_profile(self, profile_id: int) -> list[float]:
        """Return the generated load profile."""
        return self.load_profile

    def write_timeseries_data_to_db(self, results: dict[str, Any]) -> None:
        """Validate and retain a timestep result instead of persisting it."""
        self.results.append(SimTimestep(**results))

    def shutdown(self) -> None:
        """Mirror the production client's lifecycle hook."""


def test_simulation_runs_and_produces_valid_timestep_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run a fixed model through the engine and validate every result shape."""
    db_client = FakeDbClient()
    monkeypatch.setattr(sim_builder, "PostgresClient", lambda *_: db_client)

    build_and_run_simulation(sim_id="1", model_id="1")

    assert len(db_client.results) == TIMESTEPS
    assert all(isinstance(result, SimTimestep) for result in db_client.results)
