import pytest

from src.workers import simulation_runner


@pytest.mark.asyncio
async def test_run_simulation_runs_the_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the simulation engine with the expected argument order."""
    calls: list[tuple[str, str]] = []

    def fake_build_and_run_simulation(sim_id: str, model_id: str) -> None:
        calls.append((sim_id, model_id))

    monkeypatch.setattr(
        simulation_runner,
        "build_and_run_simulation",
        fake_build_and_run_simulation,
    )

    assert (
        await simulation_runner.run_simulation(sim_id="sim-1", model_id="model-1")
        is None
    )
    assert calls == [("sim-1", "model-1")]


@pytest.mark.asyncio
async def test_run_simulation_propagates_engine_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Propagate errors raised by the simulation engine."""

    def fail_build_and_run_simulation(sim_id: str, model_id: str) -> None:
        raise RuntimeError("simulation failed")

    monkeypatch.setattr(
        simulation_runner,
        "build_and_run_simulation",
        fail_build_and_run_simulation,
    )

    with pytest.raises(RuntimeError, match="simulation failed"):
        await simulation_runner.run_simulation(sim_id="sim-1", model_id="model-1")
