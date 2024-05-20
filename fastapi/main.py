import logging
import pandas as pd

from datetime import datetime
from enum import Enum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.models import (
    SimUserInputForm,
)
from database.mongodb import MongoClient
from utils.user_input_funcs import process_sim_user_input, start_ferntree_simulation


class RoofTilt(int, Enum):
    flat = 0
    tilted30 = 30
    tilted45 = 45


class RoofAzimuth(int, Enum):
    south = 0
    south_east = -45
    south_west = 45
    east = -90
    west = 90
    north_east = -135
    north_west = 135
    north = 180


# Set up logger
LOGGERNAME = "fastapi_logger"
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(LOGGERNAME)

# Create a FastAPI instance
app = FastAPI()

# Create a MongoDB client
db_client = MongoClient()

# Configure CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.post("/dashboard/pv-calc")
@app.get("/dashboard/pv-calc")
async def pv_calc(
    sim_user_input: SimUserInputForm = SimUserInputForm(
        **{
            "location": "Rütmattstrasse 17, Aarau, Switzerland",  # "Aarau, Switzerland" "Ferntree Gully, Victoria, Australia"
            "electr_cons": 3000,
            "roof_incl": RoofTilt.tilted30,
            "roof_azimuth": RoofAzimuth.south,
            "peak_power": 5,
            "battery_cap": 10,
            "electr_price": 0.25,
            "down_payment": 1000,
            "pay_off_rate": 0.1,
            "interest_rate": 5,
        }
    ),
):
    starttime = datetime.now()

    logger.info(f"\nReceived request: {sim_user_input}")

    # Determine user_id
    user_id = 123

    # Process user input and write to database
    sim_id, model_id = await process_sim_user_input(db_client, sim_user_input, user_id)

    # Start ferntree simulation
    sim_run = await start_ferntree_simulation(sim_id, model_id)
    if not sim_run:
        return {"status": "Ferntree simulation failed."}

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

    break_even_year = df[df["cumulative_profit"] > total_investment]["year"].iloc[0]

    # Add financial KPIs to results, store all KPIs and model specs as one document in results collection

    # return {"status": "Simulation started", "model": sim_model.model_dump()}

    logger.info(
        f"Total execution time: {(datetime.now() - starttime).total_seconds():.2f} seconds"
    )

    return {
        "status": "Simulation finished",
        "total_investment": float(total_investment),
        "break_even_year": int(break_even_year),
        "model_summary": model_summary,
        "sim_analysis": sim_analysis,
        "cumulative_profit": [float(profit) for profit in df["cumulative_profit"]],
    }
