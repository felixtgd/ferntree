from datetime import datetime, timezone

import pytest
import pytest_asyncio

from src.database.models import (
    PV,
    Baseload,
    Battery,
    BatteryCtrl,
    EnergyKPIs,
    FinFormData,
    FinInvestment,
    FinKPIs,
    FinResults,
    FinYearlyData,
    PVMonthlyGen,
    SimDataIn,
    SimResultsEval,
    SystemSettings,
)
from src.database.postgres import Database, pool


@pytest_asyncio.fixture(scope="module")
async def database():
    """Provide one PostgreSQL pool for the module's async tests."""
    await pool.open(wait=True)
    try:
        yield Database()
    finally:
        await pool.close()


@pytest.mark.asyncio(loop_scope="module")
async def test_database_round_trips_and_cascades(database: Database) -> None:
    """Verify typed round trips, idempotent upserts, and cascade deletion."""
    model_id = await database.insert_model(
        {
            "user_id": "mvp-user",
            "model_name": "pytest",
            "location": "Berlin",
            "roof_incl": 30,
            "roof_azimuth": 0,
            "electr_cons": 3500.0,
            "peak_power": 5.0,
            "battery_cap": 5.0,
            "coordinates": {"lat": "52.5", "lon": "13.4", "display_name": "Berlin"},
        }
    )
    try:
        model = await database.fetch_model_by_id(model_id, "mvp-user")
        assert model.model_id == model_id
        assert model.coordinates is not None

        simulation = SimDataIn(
            model_id=model_id,
            run_time=datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
            T_amb=[1.0],
            G_i=[2.0],
            coordinates={"lat": "52.5", "lon": "13.4", "display_name": "Berlin"},
            timezone="Europe/Berlin",
            timebase=3600,
            planning_horizon=1,
            system_settings=SystemSettings(
                baseload=Baseload(annual_consumption=3500, profile_id=1),
                pv=PV(roof_tilt=30, roof_azimuth=0, peak_power=5),
                battery=Battery(
                    capacity=5,
                    max_power=5,
                    soc_init=0.5,
                    battery_ctrl=BatteryCtrl(useable_capacity=0.8),
                ),
            ),
        )
        simulation_id = await database.upsert_simulation(simulation, "mvp-user")
        assert simulation_id == await database.upsert_simulation(simulation, "mvp-user")

        evaluation = SimResultsEval(
            model_id=model_id,
            energy_kpis=EnergyKPIs(
                annual_consumption=1,
                pv_generation=2,
                grid_consumption=3,
                grid_feed_in=4,
                self_consumption=5,
                self_consumption_rate=6,
                self_sufficiency=7,
            ),
            pv_monthly_gen=[PVMonthlyGen(month="Jan", pv_generation=2)],
        )
        evaluation_id = await database.upsert_sim_results_eval(evaluation, "mvp-user")
        assert await database.fetch_sim_results_eval(model_id, "mvp-user") == evaluation
        assert evaluation_id == await database.upsert_sim_results_eval(
            evaluation, "mvp-user"
        )

        finances = FinFormData(
            model_id=model_id,
            electr_price=1,
            feed_in_tariff=2,
            pv_price=3,
            battery_price=4,
            useful_life=5,
            module_deg=6,
            inflation=7,
            op_cost=8,
            down_payment=9,
            pay_off_rate=10,
            interest_rate=11,
        )
        finance_id = await database.upsert_finances(finances, "mvp-user")
        assert await database.fetch_finances(model_id, "mvp-user") == finances
        assert finance_id == await database.upsert_finances(finances, "mvp-user")

        results = FinResults(
            model_id=model_id,
            fin_kpis=FinKPIs(
                investment=FinInvestment(pv=1, battery=2, total=3),
                break_even_year=4,
                cum_profit=5,
                cum_cost_savings=6,
                cum_feed_in_revenue=7,
                cum_operation_costs=8,
                lcoe=9,
                solar_interest_rate=10,
                loan=11,
                loan_paid_off=12,
            ),
            yearly_data=[FinYearlyData(year=0, cum_profit=1, cum_cash_flow=2, loan=3)],
        )
        result_id = await database.upsert_fin_results(results, "mvp-user")
        assert await database.fetch_fin_results(model_id, "mvp-user") == results
        assert result_id == await database.upsert_fin_results(results, "mvp-user")

        assert await database.delete_model(model_id, "mvp-user")
        assert await database.fetch_sim_results_eval(model_id, "mvp-user") is None
        assert await database.fetch_finances(model_id, "mvp-user") is None
        assert await database.fetch_fin_results(model_id, "mvp-user") is None
    finally:
        await database.delete_model(model_id, "mvp-user")


@pytest.mark.asyncio(loop_scope="module")
async def test_database_rejects_unknown_or_malformed_model(database: Database) -> None:
    """Verify unknown users and malformed model IDs are handled safely."""
    assert not await database.check_user_exists("unknown-user")
    assert not await database.delete_model("not-an-integer", "mvp-user")
    with pytest.raises(RuntimeError):
        await database.fetch_model_by_id("not-an-integer", "mvp-user")
