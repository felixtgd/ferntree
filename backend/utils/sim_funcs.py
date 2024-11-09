import subprocess
from datetime import datetime
from subprocess import CompletedProcess
from typing import Any, Hashable, Optional, Union

import pandas as pd
from fastapi import HTTPException, status
from pandas import DataFrame, Series

from backend.database import mongodb
from backend.database.models import (
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
    ModelDataOut,
    PVMonthlyGen,
    SimDataIn,
    SimResultsEval,
    SystemSettings,
)
from backend.solar_data import geolocator, pvgis_api


async def get_sim_input_data(model_data: ModelDataOut) -> SimDataIn:
    """Fetch and prepare simulation input data based on the provided model data.

    This function retrieves solar data for the given location, determines the timezone,
    and defines the energy system settings based on the model data.

    Args:
        model_data (ModelDataOut): The model data containing location and
                                    system specifications.

    Returns:
        SimDataIn: The prepared simulation input data.

    Raises:
        ValueError: If there's an error fetching solar data.

    """
    # Pass parameters to pvgis_api to query solar data for sim input
    try:
        T_amb: list[float]
        G_i: list[float]
        coordinates: dict[str, str]
        T_amb, G_i, coordinates = await pvgis_api.get_solar_data_for_location(
            model_data.location, model_data.roof_azimuth, model_data.roof_incl
        )
    except Exception as ex:
        raise ValueError(f"Error fetching solar data: {ex}")

    # TODO: overwrite coordinates with data fetched in frontend
    # (querying Nominatim in backend is not working on Render)
    if model_data.coordinates:
        coordinates = model_data.coordinates.model_dump()

    # Determine timezone based on coordinates
    timezone: str = await geolocator.get_timezone(coordinates)

    # Define energy system settings based on model data
    system_settings: SystemSettings = await def_system_settings(model_data)

    sim_input_data: SimDataIn = SimDataIn(
        model_id=model_data.model_id,
        run_time=datetime.now().isoformat(),
        T_amb=T_amb,
        G_i=G_i,
        coordinates=coordinates,
        timezone=timezone,
        timebase=3600,
        planning_horizon=1,
        system_settings=system_settings,
    )

    return sim_input_data


async def def_system_settings(model_data: ModelDataOut) -> SystemSettings:
    """Define system settings based on the provided model data.

    This function creates instances of Baseload, PV, BatteryCtrl, and Battery
    using the specifications from the model data.

    Args:
        model_data (ModelDataOut): The model data containing system specifications.

    Returns:
        SystemSettings: The defined system settings.

    """
    baseload: Baseload = Baseload(
        annual_consumption=model_data.electr_cons,
        profile_id=1,  # TODO: Find better way to set profile_id
    )

    pv: PV = PV(
        roof_tilt=model_data.roof_incl,
        roof_azimuth=model_data.roof_azimuth,
        peak_power=model_data.peak_power,
    )

    battery_ctrl: BatteryCtrl = BatteryCtrl(
        planning_horizon=1,
        useable_capacity=0.8,
        greedy=True,
        opt_fill=False,
    )

    battery: Battery = Battery(
        capacity=model_data.battery_cap,
        max_power=model_data.battery_cap,  # TODO: Add max_power to user input?
        soc_init=model_data.battery_cap * 0.1,
        battery_ctrl=battery_ctrl,
    )

    system_settings: SystemSettings = SystemSettings(
        baseload=baseload,
        pv=pv,
        battery=battery,
    )

    return system_settings


async def run_ferntree_simulation(
    model_id: str,
    sim_id: str,
) -> bool:
    """Start the Ferntree simulation with the given simulation ID and model ID.

    This function runs the Ferntree simulation as a subprocess and checks if it
    completed successfully.

    Args:
        model_id (str): The model ID.
        sim_id (str): The simulation ID.

    Returns:
        bool: True if the simulation was successful.

    Raises:
        RuntimeError: If the simulation fails.

    """
    command: list[str] = [
        "python",
        "sim/ferntree/ferntree.py",
        "--sim_id",
        sim_id,
        "--model_id",
        model_id,
    ]
    completed_process: CompletedProcess[Any] = subprocess.run(command)

    # Check if the simulation has finished successfully
    if completed_process.returncode != 0:
        raise RuntimeError(
            f"Ferntree Simulation failed. Return code: {completed_process.returncode}"
        )

    return True


async def eval_sim_results(
    db_client: mongodb.MongoClient, model_id: str
) -> SimResultsEval:
    """Evaluate simulation results for a given model.

    This function fetches simulation results from the database, calculates energy KPIs,
    and computes monthly PV generation data.

    Args:
        db_client (mongodb.MongoClient): The MongoDB client.
        model_id (str): The ID of the model to evaluate.

    Returns:
        SimResultsEval: The evaluated simulation results.

    Raises:
        RuntimeError: If fetching simulation results fails.

    """
    # Fetch sim results timeseries data
    doc: Optional[dict[str, Any]] = await db_client.fetch_document(
        "sim_results_ts", model_id
    )
    if doc is None:
        raise RuntimeError(
            f"Failed to fetch sim results timeseries for model_id {model_id}"
        )
    sim_results_dict: list[dict[str, float]] = doc["timeseries"]

    energy_kpis: EnergyKPIs = await calc_energy_kpis(sim_results_dict)
    pv_monthly_gen: list[PVMonthlyGen] = await calc_pv_monthly_gen(sim_results_dict)

    sim_results_eval: SimResultsEval = SimResultsEval(
        model_id=model_id,
        energy_kpis=energy_kpis,
        pv_monthly_gen=pv_monthly_gen,
    )

    return sim_results_eval


async def calc_energy_kpis(sim_results: list[dict[str, float]]) -> EnergyKPIs:
    """Calculate energy Key Performance Indicators (KPIs) from simulation results.

    This function processes the simulation results to compute various energy KPIs
    such as annual PV generation, self-consumption, and self-sufficiency.

    Args:
        sim_results (list[dict[str, float]]): The simulation results data.

    Returns:
        EnergyKPIs: The calculated energy KPIs.

    """
    # Read sim results into dataframe
    sim_results_df: DataFrame = pd.DataFrame(sim_results)

    # Set time column to datetime, measured in seconds
    sim_results_df["time"] = pd.to_datetime(sim_results_df["time"], unit="s")
    # Set time column as index
    sim_results_df.set_index("time", inplace=True)

    # Calculate net load of house with baseload and pv generation
    sim_results_df["P_net_load"] = (
        sim_results_df["P_base"] + sim_results_df["P_pv"]
    )  # + sim_results_df["P_heat_el"]
    # Calculate total power profile of house with net load and battery power
    sim_results_df["P_total"] = sim_results_df["P_net_load"] + sim_results_df["P_bat"]

    # Calculate energy KPIs of system simulation
    # Annual electricity consumption from baseload demand
    annual_baseload_demand: float = sim_results_df["P_base"].sum()  # [kWh]
    # Annaul PV generation
    annual_pv_generation: float = (
        abs(sim_results_df["P_pv"].sum()) + sim_results_df["Soc_bat"].iloc[-1]
    )  # [kWh]
    # Annaul electricity consumed fron grid
    annual_grid_consumption: float = sim_results_df["P_total"][
        sim_results_df["P_total"] > 0.0
    ].sum()  # [kWh]
    # Annual electricity fed into grid
    annual_grid_feed_in: float = abs(
        sim_results_df["P_total"][sim_results_df["P_total"] < 0.0].sum()
    )  # [kWh]
    # Annual amount of energy consumption covered by PV generation
    annual_self_consumption: float = annual_baseload_demand - annual_grid_consumption

    # Energy KPIs of system simulation
    energy_kpis: EnergyKPIs = EnergyKPIs(
        annual_consumption=annual_baseload_demand,
        pv_generation=annual_pv_generation,
        grid_consumption=annual_grid_consumption,
        grid_feed_in=annual_grid_feed_in,
        self_consumption=annual_self_consumption,
        self_consumption_rate=annual_self_consumption / annual_pv_generation
        if annual_pv_generation > 0
        else 0,
        self_sufficiency=annual_self_consumption / annual_baseload_demand
        if annual_baseload_demand > 0
        else 0,
    )

    return energy_kpis


async def calc_pv_monthly_gen(sim_results: list[dict[str, Any]]) -> list[PVMonthlyGen]:
    """Calculate monthly PV generation data from simulation results.

    This function processes the simulation results to compute the total PV generation
    for each month of the year.

    Args:
        sim_results (list[dict[str, Any]]): The simulation results data.

    Returns:
        list[PVMonthlyGen]: A list of monthly PV generation data.

    Raises:
        ValueError: If the time index in the data is not a datetime index.

    """
    # Convert timeseries data to dataframe
    df: DataFrame = pd.DataFrame(sim_results)

    # Set time column to datetime, measured in seconds
    df["time"] = pd.to_datetime(df["time"], unit="s")
    # Set time column as index
    df.set_index("time", inplace=True)

    # Verify the index is a datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Index is not a datetime index")

    # Group by month and sum P_pv values
    df["month"] = df.index.month
    monthly_pv_df: Series[float] = df.groupby("month")["P_pv"].sum()

    month_mapping: dict[Hashable, str] = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }

    # Convert monthly PV generation data to list of dictionaries
    pv_monthly_gen: list[PVMonthlyGen] = [
        PVMonthlyGen(month=month_mapping[index], pv_generation=-1 * pv_gen)
        for index, pv_gen in monthly_pv_df.items()
    ]

    return pv_monthly_gen


async def calc_fin_results(
    db_client: mongodb.MongoClient,
    fin_data: FinFormData,
) -> FinResults:
    """Calculate financial results based on simulation results and financial input data.

    This function fetches model data and simulation results, then performs financial
    calculations including investment costs, profits, and various financial KPIs.

    Args:
        db_client (mongodb.MongoClient): The MongoDB client.
        fin_data (FinFormData): The financial input data.

    Returns:
        FinResults: The calculated financial results.

    Raises:
        HTTPException: If simulation results are not found.

    """
    # Fetch model data from database
    model_data: ModelDataOut = await db_client.fetch_model_by_id(fin_data.model_id)

    # Fetch sim results evaluation from database
    doc: Optional[dict[str, Any]] = await db_client.fetch_document(
        "sim_results_eval", model_data.model_id
    )
    sim_results_eval: Optional[SimResultsEval] = SimResultsEval(**doc) if doc else None
    if sim_results_eval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation results not found.",
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
