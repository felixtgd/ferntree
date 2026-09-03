import asyncio

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


async def main() -> None:
    """Exercise the PostgreSQL API data layer end to end.

    Returns:
        None: This function raises an assertion error if a check fails.

    """
    db = Database()
    await pool.open()
    try:
        model_id = await db.insert_model(
            {
                "user_id": "mvp-user",
                "model_name": "smoke",
                "location": "Berlin",
                "roof_incl": 30,
                "roof_azimuth": 0,
                "electr_cons": 3500.0,
                "peak_power": 5.0,
                "battery_cap": 5.0,
                "coordinates": {"lat": "52.5", "lon": "13.4", "display_name": "Berlin"},
            }
        )
        model = await db.fetch_model_by_id(model_id, "mvp-user")
        assert model.model_id == model_id and model.user_id == "mvp-user"

        simulation = SimDataIn(
            model_id=model_id,
            run_time="2026-01-01T00:00:00+00:00",
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
        simulation_id = await db.upsert_simulation(simulation, "mvp-user")
        assert simulation_id == await db.upsert_simulation(simulation, "mvp-user")

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
        evaluation_id = await db.upsert_sim_results_eval(evaluation, "mvp-user")
        assert evaluation == await db.fetch_sim_results_eval(model_id, "mvp-user")
        assert evaluation_id == await db.upsert_sim_results_eval(evaluation, "mvp-user")

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
        finance_id = await db.upsert_finances(finances, "mvp-user")
        assert finances == await db.fetch_finances(model_id, "mvp-user")
        assert finance_id == await db.upsert_finances(finances, "mvp-user")

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
        result_id = await db.upsert_fin_results(results, "mvp-user")
        assert results == await db.fetch_fin_results(model_id, "mvp-user")
        assert result_id == await db.upsert_fin_results(results, "mvp-user")

        assert await db.delete_model(model_id, "mvp-user")
        print("Stage 3 database smoke test passed")
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
