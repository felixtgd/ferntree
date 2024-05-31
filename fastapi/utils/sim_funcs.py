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
    SimEnergyKPIs,
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

    # Write sim input data as one document to sim_timeseries collection in MongoDB, return sim_id
    created_at = datetime.now().isoformat()
    document_solar_data = SimTimeSeriesDoc(
        user_id=user_id,
        created_at=created_at,
        T_amb=T_amb,
        G_i=G_i,
    )
    sim_id = await db_client.insert_one(
        collection="sim_timeseries", document=document_solar_data.model_dump()
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


async def get_model_summary(sim_user_input: SimUserInputForm) -> SimModelSummary:
    """Creates a model summary with the most important model specifications.
    - Extracts the most important model specifications from the user input form
    - Creates a SimModelSummary response model with the model specifications

    Args:
        sim_user_input (SimUserInputForm): The user input form.

    Returns:
        SimModelSummary: The model summary with the most important model specifications.

    """
    # Create SimModelSummary response model with sim model specifications
    model_summary = SimModelSummary(
        electr_cons=sim_user_input.electr_cons,  # [kWh]
        pv_power=sim_user_input.peak_power,  # [kWp]
        battery_capacity=sim_user_input.battery_cap,  # [kWh]
        electr_price=sim_user_input.electr_price / 100,  # user input in cents, need €
        down_payment=sim_user_input.down_payment / 100,  # user input in %, need 0...1
        pay_off_rate=sim_user_input.pay_off_rate / 100,  # user input in %, need 0...1
        interest_rate=sim_user_input.interest_rate / 100,  # user input in %, need 0...1
    )

    return model_summary


async def calc_energy_kpis(
    db_client: mongodb.MongoClient, sim_id: str
) -> SimEnergyKPIs:
    """Calculates the energy KPIs of the simulation results.
    - Reads the simulation results from the database
    - Calculates various energy KPIs, e.g. annual pv generation, self-consumption, self-sufficiency

    Args:
        db_client (MongoClient): The MongoDB client.
        sim_id (str): The simulation ID.

    Returns:
        SimEnergyKPIs: The energy KPIs of the simulation results.

    """
    # Read sim results from db into dataframe
    sim_results = await db_client.find_one_by_id("sim_timeseries", sim_id)
    sim_results_df = pd.DataFrame(sim_results["timeseries_data"])

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
    annual_baseload_demand = sim_results_df["P_base"].sum()  # [kWh]
    # Annaul PV generation
    annual_pv_generation = (
        abs(sim_results_df["P_pv"].sum()) + sim_results_df["Soc_bat"].iloc[-1]
    )  # [kWh]
    # Annaul electricity consumed fron grid
    annual_grid_consumption = sim_results_df["P_total"][
        sim_results_df["P_total"] > 0.0
    ].sum()  # [kWh]
    # Annual electricity fed into grid
    annual_grid_feed_in = abs(
        sim_results_df["P_total"][sim_results_df["P_total"] < 0.0].sum()
    )  # [kWh]
    # Annual amount of energy consumption covered by PV generation
    annual_self_consumption = annual_baseload_demand - annual_grid_consumption

    # Energy KPIs of system simulation
    sim_energy_kpis = SimEnergyKPIs(
        baseload_demand=annual_baseload_demand,
        pv_generation=annual_pv_generation,
        grid_consumption=annual_grid_consumption,
        grid_feed_in=annual_grid_feed_in,
        self_consumption=annual_self_consumption,
        self_consumption_rate=annual_self_consumption / annual_pv_generation,
        self_sufficiency=annual_self_consumption / annual_baseload_demand,
    )

    return sim_energy_kpis


async def calc_financial_analysis(
    model_summary: SimModelSummary, sim_energy_kpis: SimEnergyKPIs
) -> SimFinancialAnalysis:
    """Calculates the financial analysis of the energy system based on the model summary and energy KPIs.
    - Sets assumptions for financial performance calculation
    - Calculates investment costs for PV and battery system
    - Calculates financial performance of energy system over 30 years
    - Calculates financial KPIs, e.g. break-even year

    Args:
        model_summary (SimModelSummary): The model summary.
        sim_energy_kpis (SimEnergyKPIs): The energy KPIs.

    Returns:
        SimFinancialAnalysis: The financial analysis of the energy system.

    """
    # Assumptions for financial performance calculation
    financial_assumptions = SimFinancialAssumptions(
        price_increase=0.025,  # annual (electricity) price increase 2.5%
        pv_costs_per_kWp=1700,  # €/kWp for PV system (1563 - 2167) TODO: model this as a function of peak_power
        battery_costs_per_kWh=650,  # €/kWh for battery system (570 - 732) TODO: model this as a function of battery_cap
        module_degradation=0.01,  # annual module degradation 1%
        operation_costs=0.015,  # annual operation costs 1.5% (insurance, maintenance, etc.)
        feed_in_tariff=0.08,  # €/kWh feed-in tariff
    )

    # Investment costs
    pv_investment = model_summary.pv_power * financial_assumptions.pv_costs_per_kWp
    battery_investment = (
        model_summary.battery_capacity * financial_assumptions.battery_costs_per_kWh
    )
    total_investment = pv_investment + battery_investment
    investment = SimFinancialInvestment(
        pv=pv_investment,
        battery=battery_investment,
        total=total_investment,
    )

    # Dataframe for fincancial calculations
    df = pd.DataFrame()
    # Calculate financial performance of energy system over 30 years
    df["year"] = range(31)
    # Energy consumption assumed to stay constant
    df["consumption"] = sim_energy_kpis.baseload_demand  # [kWh]
    # Electricity price increases annually by price_increase
    df["electr_price"] = (
        model_summary.electr_price
        * (1 + financial_assumptions.price_increase) ** df["year"]
    )  # [€/kWh]
    # PV generation decreases annually by module_degradation
    df["pv_generation"] = (
        sim_energy_kpis.pv_generation
        * (1 - financial_assumptions.module_degradation) ** df["year"]
    )  # [kWh]
    # Self-consumption: amount PV generation consumed on-site (sc-rate stays constant)
    df["self_consumption"] = (
        df["pv_generation"] * sim_energy_kpis.self_consumption_rate
    )  # [kWh]
    # Cost savings due to self-consumed PV generation (as compared to scenario without PV)
    df["electr_cost_savings"] = df["self_consumption"] * df["electr_price"]  # [€]
    # Revenue from grid feed-in of remaining/unused PV generation
    df["feed_in_remuneration"] = (
        df["pv_generation"] - df["self_consumption"]
    ) * financial_assumptions.feed_in_tariff  # [€]
    # Operation costs: maintenance, insurance etc.
    df["operation_costs"] = (
        total_investment
        * financial_assumptions.operation_costs
        * (1 + financial_assumptions.price_increase) ** df["year"]
    )  # [€]
    # Profit from cost savings and feed-in minus operation costs
    df["profit"] = (
        df["electr_cost_savings"] + df["feed_in_remuneration"] - df["operation_costs"]
    )  # [€]
    df["cumulative_profit"] = df["profit"].cumsum()  # [€]

    # For now only one financial KPI: Break-even year
    # TODO: Add more KPIs in the future
    break_even_year = df[df["cumulative_profit"] > total_investment]["year"].iloc[0]

    financial_kpis = SimFinancialKPIs(
        break_even_year=break_even_year,
    )

    # Collect everything in one response model
    financial_analysis = SimFinancialAnalysis(
        assumptions=financial_assumptions,
        investment=investment,
        kpis=financial_kpis,
    )

    return financial_analysis


async def evaluate_simulation_results(
    db_client: mongodb.MongoClient, sim_id: str, sim_user_input: SimUserInputForm
) -> tuple[str, SimEvaluationDoc]:
    """Evaluates the simulation results and writes the evaluation to the database.
    - Reads the timeseries simulation results from the database
    - Calculates energy KPIs, e.g. annual pv generation, self-consumption, self-sufficiency
    - Calculates financial KPIs, e.g. break-even year
    - Writes the evaluation to the database

    Args:
        db_client (MongoClient): The MongoDB client.
        sim_id (str): The simulation ID.
        sim_user_input (SimUserInputForm): The user input form.

    Returns:
        tuple[str, SimEvaluationDoc]: The simulation evaluation ID and the simulation evaluation document.

    """
    # Get model summary with most important models specs
    model_summary = await get_model_summary(sim_user_input)

    # Evaluate simulation results and calculate energy KPIs
    sim_energy_kpis = await calc_energy_kpis(db_client, sim_id)

    # Use model specs and energy KPIs to calc financial analysis of energy system
    sim_financial_analysis = await calc_financial_analysis(
        model_summary, sim_energy_kpis
    )

    # Collect all results in one document to store in database
    sim_evaluation = SimEvaluationDoc(
        sim_id=sim_id,
        sim_model_summary=model_summary,
        energy_kpis=sim_energy_kpis,
        financial_analysis=sim_financial_analysis,
    )

    # Write sim evaluation to database
    sim_eval_id = await db_client.insert_one(
        collection="sim_evaluation", document=sim_evaluation.model_dump()
    )

    return sim_eval_id, sim_evaluation
