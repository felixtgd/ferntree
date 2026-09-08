from typing import Any, Hashable

import pandas as pd
from pandas import DataFrame, Series

from src.db.schemas import EnergyKPIs, PVMonthlyGen, SimResultsEval
from src.domains.energy.ports import TimestepReader


async def eval_sim_results(
    db: TimestepReader, model_id: str, user_id: int
) -> SimResultsEval:
    """Evaluate simulation results for a given model.

    This function fetches simulation results from the database, calculates energy KPIs,
    and computes monthly PV generation data.

    Args:
        db (TimestepReader): The persistence reader.
        model_id (str): The ID of the model to evaluate.
        user_id (int): The user id requesting the evaluation.

    Returns:
        SimResultsEval: The evaluated simulation results.

    Raises:
        RuntimeError: If fetching simulation results fails.

    """
    # Fetch sim results timeseries data
    sim_results_dict: list[dict[str, float]] = await db.fetch_timesteps(
        model_id, user_id
    )
    if not sim_results_dict:
        raise RuntimeError(
            f"Failed to fetch sim results timeseries for model_id {model_id}"
        )

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
