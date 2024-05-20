from datetime import datetime
import os
import subprocess
import pandas as pd

from database.models import (
    SimUserInputForm,
    SimTimeSeriesDoc,
    SimModelSpecsDoc,
    SimEvaluationDoc,
    SimModelSummary,
    SimAnalysis,
    SimFinancialAnalysis,
    SimFinancialAssumptions,
    SimFinancialInvestment,
    SimFinancialKPIs,
)
from database import mongodb
from solar_data import pvgis_api, geolocator
from utils import data_model_helpers


async def process_sim_user_input(
    db_client: mongodb.MongoClient, sim_user_input: SimUserInputForm, user_id: int
) -> tuple[str, str]:
    """Processes the user input for the simulation.
    - Fetches solar data for the location from PVGIS API
    - Writes the solar data and model specs to the database (both input for simulation)
    - Returns the sim_id and model_id

    Args:
        db_client (MongoClient): The MongoDB client.
        sim_user_input (SimUserInputForm): The user input form.
        user_id (int): The user ID.

    Returns:
        tuple[str, str]: The simulation ID and model ID.

    """
    # Get address, roof azimuth and tilt from model specs
    location = sim_user_input.location
    roof_azimuth = sim_user_input.roof_azimuth
    roof_incl = sim_user_input.roof_incl

    # Pass parameters to pvgis_api to query solar data for sim input
    try:
        T_amb, G_i, coordinates = await pvgis_api.get_solar_data_for_location(
            location, roof_azimuth, roof_incl
        )
    except Exception as ex:
        raise ValueError(f"Error fetching solar data: {ex}")

    # Write sim input data as one document to simulation_timeseries collection in MongoDB, return sim_id
    created_at = datetime.now().isoformat()
    document_solar_data = SimTimeSeriesDoc(
        user_id=user_id,
        created_at=created_at,
        T_amb=T_amb,
        G_i=G_i,
    )
    sim_id = await db_client.insert_one(
        collection="simulation_timeseries", document=document_solar_data.model_dump()
    )

    # Determine timezone based on coordinates
    timezone = await geolocator.get_timezone(coordinates)

    # Define model_specs for the simulation and write to database
    sim_model_specs = await data_model_helpers.define_sim_model_specs(
        sim_user_input, coordinates, timezone
    )
    document_model_specs = SimModelSpecsDoc(
        user_id=user_id,
        sim_id=sim_id,
        created_at=created_at,
        sim_model_specs=sim_model_specs,
    )

    # Write model_specs to model_specs_coll in MongoDB
    model_id = await db_client.insert_one(
        collection="model_specs", document=document_model_specs.model_dump()
    )

    return sim_id, model_id


async def start_ferntree_simulation(sim_id: str, model_id: str) -> bool:
    """Starts the Ferntree simulation with the given sim_id and model_id.

    Args:
        sim_id (str): The simulation ID.
        model_id (str): The model ID.

    Returns:
        bool: True if the simulation was successful.

    """
    script_dir = os.path.dirname(__file__)
    ferntree_sim_dir = os.path.join(script_dir, "../../sim/ferntree/")
    command = [
        "python",
        "ferntree.py",
        "--sim_id",
        sim_id,
        "--model_id",
        model_id,
    ]
    completed_process = subprocess.run(command, cwd=ferntree_sim_dir)

    # Check if the simulation has finished successfully
    if completed_process.returncode != 0:
        raise ValueError(
            f"Ferntree Simulation failed. Return code: {completed_process.returncode}"
        )

    return True


async def evaluate_simulation_results(
    db_client: mongodb.MongoClient, sim_id: str, sim_user_input: SimUserInputForm
) -> tuple[str, SimEvaluationDoc]:
    """Evaluates the simulation results and writes the evaluation to the database.
    - Reads the timeseries simulation results from the database
    - Calculates simulation KPIs, e.g. annual pv generation, self-consumption, self-sufficiency
    - Calculates financial KPIs, e.g. break-even year
    - Writes the evaluation to the database

    Args:
        db_client (MongoClient): The MongoDB client.
        sim_id (str): The simulation ID.
        sim_user_input (SimUserInputForm): The user input form.

    Returns:
        tuple[str, SimEvaluationDoc]: The simulation evaluation ID and the simulation evaluation document.

    """
    # TODO: THIS FUNCTION NEEDS TO REFACTORING!!!
    # Read sim results from db and calculate system KPIs
    sim_results = await db_client.find_one_by_id("simulation_timeseries", sim_id)

    sim_results_df = pd.DataFrame(sim_results["timeseries_data"])
    # Set time column to datetime, measured in seconds
    sim_results_df["time"] = pd.to_datetime(sim_results_df["time"], unit="s")
    # Set time column as index
    sim_results_df.set_index("time", inplace=True)

    sim_results_df["P_net_load"] = (
        sim_results_df["P_base"] + sim_results_df["P_pv"]
    )  # + sim_results_df["P_heat_el"]
    sim_results_df["P_total"] = sim_results_df["P_net_load"] + sim_results_df["P_bat"]

    annual_baseload_demand = sim_results_df["P_base"].sum()
    annual_pv_generation = (
        abs(sim_results_df["P_pv"].sum()) + sim_results_df["Soc_bat"].iloc[-1]
    )
    annual_grid_consumption = sim_results_df["P_total"][
        sim_results_df["P_total"] > 0.0
    ].sum()
    annual_grid_feed_in = abs(
        sim_results_df["P_total"][sim_results_df["P_total"] < 0.0].sum()
    )
    annual_self_consumption = annual_baseload_demand - annual_grid_consumption

    # Create results dictionary with model specifications, simulation results and financial results
    model_summary = {
        "electr_cons": sim_user_input.electr_cons,
        "pv_power": sim_user_input.peak_power,
        "battery_capacity": sim_user_input.battery_cap,
        "electr_price": sim_user_input.electr_price,
        "down_payment": sim_user_input.down_payment,
        "pay_off_rate": sim_user_input.pay_off_rate,
        "interest_rate": sim_user_input.interest_rate,
    }

    sim_analysis = {
        "baseload_demand": annual_baseload_demand,
        "pv_generation": annual_pv_generation,
        "grid_consumption": annual_grid_consumption,
        "grid_feed_in": annual_grid_feed_in,
        "self_consumption": annual_self_consumption,
        "self_consumption_rate": annual_self_consumption / annual_pv_generation,
        "self_sufficiency": annual_self_consumption / annual_baseload_demand,
    }

    # Compute financial perfomance with model_specs and system KPIs, write results to financial collection

    # Assumptions for financial performance calculation
    price_increase = 0.025  # annual (electricity) price increase 2.5%
    pv_costs_per_kWp = 1700  # €/kWp for PV system (1563 - 2167) TODO: model this as a function of peak_power
    battery_costs_per_kWh = 650  # €/kWh for battery system (570 - 732) TODO: model this as a function of battery_cap
    module_degradation = 0.01  # annual module degradation 1%
    operation_costs = (
        0.015  # annual operation costs 1.5% (insurance, maintenance, etc.)
    )
    feed_in_tariff = 0.08  # €/kWh feed-in tariff

    # Investment costs
    pv_investment = sim_user_input.peak_power * pv_costs_per_kWp
    battery_investment = sim_user_input.battery_cap * battery_costs_per_kWh
    total_investment = pv_investment + battery_investment

    # Dataframe for fincancial calculations
    df = pd.DataFrame()
    df["year"] = range(31)
    df["consumption"] = annual_baseload_demand  # annual electricity consumption in kWh
    df["electr_price"] = (
        sim_user_input.electr_price * (1 + price_increase) ** df["year"]
    )  # electricity price in €/kWh
    df["pv_generation"] = (
        annual_pv_generation * (1 - module_degradation) ** df["year"]
    )  # annual PV generation in kWh
    df["self_consumption"] = (
        df["pv_generation"] * sim_analysis["self_consumption_rate"]
    )  # annual self-consumption in kWh (the amount of PV generation that is consumed on-site)
    df["electr_cost_savings"] = (
        df["self_consumption"] * df["electr_price"]
    )  # annual electricity cost savings in €
    df["feed_in_remuneration"] = (
        df["pv_generation"] - df["self_consumption"]
    ) * feed_in_tariff  # annual feed-in remuneration in €
    df["operation_costs"] = (
        total_investment * operation_costs * (1 + price_increase) ** df["year"]
    )  # annual operation costs in €
    df["profit"] = (
        df["electr_cost_savings"] + df["feed_in_remuneration"] - df["operation_costs"]
    )  # annual profit in €
    df["cumulative_profit"] = df["profit"].cumsum()

    # For now only one financial KPI: Break-even year
    # TODO: Add more KPIs in the future
    break_even_year = df[df["cumulative_profit"] > total_investment]["year"].iloc[0]

    financial_analysis = {
        "assumptions": {
            "price_increase": price_increase,
            "pv_costs_per_kWp": pv_costs_per_kWp,
            "battery_costs_per_kWh": battery_costs_per_kWh,
            "module_degradation": module_degradation,
            "operation_costs": operation_costs,
            "feed_in_tariff": feed_in_tariff,
        },
        "investment": {
            "pv": pv_investment,
            "battery": battery_investment,
            "total": total_investment,
        },
        "kpis": {
            "break_even_year": break_even_year,
        },
    }

    sim_evaluation = SimEvaluationDoc(
        sim_id=sim_id,
        sim_model_summary=SimModelSummary(**model_summary),
        sim_analysis=SimAnalysis(**sim_analysis),
        financial_analysis=SimFinancialAnalysis(
            assumptions=SimFinancialAssumptions(**financial_analysis["assumptions"]),
            investment=SimFinancialInvestment(**financial_analysis["investment"]),
            kpis=SimFinancialKPIs(**financial_analysis["kpis"]),
        ),
    )

    # Write sim evaluation to database
    sim_eval_id = await db_client.insert_one(
        collection="sim_evaluation", document=sim_evaluation.model_dump()
    )

    return sim_eval_id, sim_evaluation
