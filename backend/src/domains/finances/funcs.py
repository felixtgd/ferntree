import logging
from typing import Hashable, Union

import pandas as pd
from pandas import DataFrame

from src.db.schemas import (
    EnergyKPIs,
    FinFormData,
    FinInvestment,
    FinKPIs,
    FinResults,
    FinYearlyData,
    ModelDataOut,
)
from src.domains.finances.ports import FinanceDataReader

logger: logging.Logger = logging.getLogger("ferntree")


async def calc_fin_results(
    db: FinanceDataReader,
    fin_data: FinFormData,
    user_id: str,
) -> FinResults:
    """Calculate financial results based on simulation results and financial input data.

    This function fetches model data and simulation results, then performs financial
    calculations including investment costs, profits, and various financial KPIs.

    Args:
        db (FinanceDataReader): The persistence reader.
        fin_data (FinFormData): The financial input data.
        user_id (str): The username requesting the calculation.

    Returns:
        FinResults: The calculated financial results.

    Raises:
        RuntimeError: If simulation results are not found.

    """
    # Fetch model data from database
    model_data: ModelDataOut = await db.fetch_model_by_id(fin_data.model_id, user_id)

    # Fetch sim results evaluation from database
    sim_results_eval = await db.fetch_sim_results_eval(model_data.model_id, user_id)
    if sim_results_eval is None:
        raise RuntimeError(
            f"Simulation results not found for model {model_data.model_id}"
        )
    energy_kpis: EnergyKPIs = sim_results_eval.energy_kpis

    # Investment costs
    pv_investment: float = model_data.peak_power * fin_data.pv_price
    battery_investment: float = model_data.battery_cap * fin_data.battery_price
    total_investment: float = pv_investment + battery_investment
    investment: FinInvestment = FinInvestment(
        pv=pv_investment,
        battery=battery_investment,
        total=total_investment,
    )

    # Convert cents to €
    fin_data.electr_price /= 100
    fin_data.feed_in_tariff /= 100
    # Convert % to fractions
    fin_data.module_deg /= 100
    fin_data.inflation /= 100
    fin_data.op_cost /= 100
    fin_data.down_payment /= 100
    fin_data.pay_off_rate /= 100
    fin_data.interest_rate /= 100

    # Dataframe for fincancial calculations
    df: DataFrame = pd.DataFrame()

    # Calculate financial performance of energy system over 25 years
    years_financial_analysis: int = fin_data.useful_life
    df["year"] = range(years_financial_analysis + 1)

    # Energy consumption assumed to stay constant
    df["consumption"] = model_data.electr_cons  # [kWh]

    # Electricity price increases annually by price_increase
    df["electr_price"] = (
        fin_data.electr_price * (1 + fin_data.inflation) ** df["year"]
    )  # [€/kWh]

    # PV generation decreases annually by module_degradation
    df["pv_generation"] = (
        energy_kpis.pv_generation * (1 - fin_data.module_deg) ** df["year"]
    )  # [kWh]

    # Self-consumption: amount PV generation consumed on-site (sc-rate stays constant)
    df["self_consumption"] = (
        df["pv_generation"] * energy_kpis.self_consumption_rate
    )  # [kWh]

    # Cost savings due to self-consumed PV generation (as compared to scenario w/o PV)
    df["electr_cost_savings"] = df["self_consumption"] * df["electr_price"]  # [€]

    # Revenue from grid feed-in of remaining/unused PV generation
    df["feed_in_remuneration"] = (
        df["pv_generation"] - df["self_consumption"]
    ) * fin_data.feed_in_tariff  # [€]

    # Operation costs: maintenance, insurance etc.
    df["operation_costs"] = (
        total_investment * fin_data.op_cost * (1 + fin_data.inflation) ** df["year"]
    )  # [€]

    # Profit from cost savings and feed-in minus operation costs
    df["profit"] = (
        df["electr_cost_savings"] + df["feed_in_remuneration"] - df["operation_costs"]
    )  # [€]

    df["cumulative_profit"] = df["profit"].cumsum()  # [€]

    ## Calculate loan and cash flow
    loan: list[float] = [total_investment * (1 - fin_data.down_payment)]
    repayment: list[float] = [0.0]  # system_cost * repayment_percentage
    interest: list[float] = [loan[0] * fin_data.interest_rate]

    for year in range(len(df) - 1):
        loan_next_year: float = loan[year] - repayment[year]
        loan.append(loan_next_year if loan_next_year > 0 else 0)
        repayment.append(loan[0] * fin_data.pay_off_rate if loan_next_year > 0 else 0)
        interest.append(loan_next_year * fin_data.interest_rate)

    df["loan"] = loan
    df["repayment"] = repayment
    df["interest"] = interest
    df["capital_cost"] = df["repayment"] + df["interest"]
    df["cash_flow"] = df["profit"] - df["capital_cost"]
    df["cumulative_cash_flow"] = df["cash_flow"].cumsum()

    ## Financial KPI:

    # Loan paid off year
    try:
        loan_paid_off: int = df[df["loan"] == 0].iloc[0]["year"] - 1
    except IndexError:
        loan_paid_off = -1

    # Break-even year
    try:
        break_even_year: int = df[df["cumulative_profit"] > total_investment][
            "year"
        ].iloc[0]
        break_even_year_exact: float = (
            (break_even_year - 1)
            + (total_investment - df.iloc[break_even_year - 1]["cumulative_profit"])
            / df.iloc[break_even_year]["profit"]
            if break_even_year > 0
            else 0.0
        )
    except IndexError:
        break_even_year = -1
        break_even_year_exact = -1.0

    # Cumulative profit over 25 years
    cum_profit: float = df["cumulative_profit"].iloc[-1]

    # Cumulative cost savings over 25 years
    cum_cost_savings: float = df["electr_cost_savings"].sum()

    # Cumulative feed-in revenue over 25 years
    cum_feed_in_revenue: float = df["feed_in_remuneration"].sum()

    # Cumulative operation costs over 25 years
    cum_operation_costs: float = df["operation_costs"].sum()

    # Levelised cost of electricity
    lcoe: float = (
        (
            (total_investment + df["operation_costs"].sum())
            / df["pv_generation"].sum()
            * 100
        )
        if df["pv_generation"].sum() > 0
        else -1
    )  # [cents/kWh]

    # Solar interest rate: average annual return on investment
    df["solar_interest_rate"] = (
        (df["profit"] / total_investment * 100) if total_investment > 0 else -1
    )
    solar_interest_rate: float = df["solar_interest_rate"].mean()

    fin_kpis: FinKPIs = FinKPIs(
        investment=investment,
        break_even_year=break_even_year_exact,
        cum_profit=cum_profit,
        cum_cost_savings=cum_cost_savings,
        cum_feed_in_revenue=cum_feed_in_revenue,
        cum_operation_costs=cum_operation_costs,
        lcoe=lcoe,
        solar_interest_rate=solar_interest_rate,
        loan=loan[0],
        loan_paid_off=loan_paid_off,
    )

    fin_yearly_data_df: list[dict[Hashable, Union[float, int]]] = df[
        ["year", "cumulative_profit", "cumulative_cash_flow", "loan"]
    ].to_dict(orient="records")
    fin_yearly_data: list[FinYearlyData] = [
        FinYearlyData(
            year=int(record["year"]),
            cum_profit=float(record["cumulative_profit"]),
            cum_cash_flow=float(record["cumulative_cash_flow"]),
            loan=float(record["loan"]),
        )
        for record in fin_yearly_data_df
    ]

    # Collect everything in one response model
    fin_results: FinResults = FinResults(
        model_id=model_data.model_id,
        fin_kpis=fin_kpis,
        yearly_data=fin_yearly_data,
    )

    return fin_results
