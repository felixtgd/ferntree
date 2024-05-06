from datetime import datetime
import os
import subprocess

from database.models import (
    SimUserInputForm,
    SimTimeSeriesDoc,
    SimModelSpecsDoc,
)
from database.mongodb import MongoClient
from solar_data import pvgis_api
from utils.data_model_helpers import define_sim_model_specs


async def process_sim_user_input(
    db_client: MongoClient, sim_user_input: SimUserInputForm, user_id: int
) -> tuple[str, str]:
    # Get address, roof azimuth and tilt from model specs
    location = sim_user_input.location
    roof_azimuth = sim_user_input.roof_azimuth
    roof_incl = sim_user_input.roof_incl

    # Pass parameters to pvgis_api to query solar data for sim input
    T_amb, G_i = await pvgis_api.get_solar_data_for_location(
        location, roof_azimuth, roof_incl
    )
    if not T_amb or not G_i:
        raise ValueError("Error fetching solar data. T_amb or G_i is None.")

    # Write sim input data and model specs as one document to simulation_coll in MongoDB, return sim_id
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

    # Define model_specs for the simulation and write to database
    sim_model_specs = await define_sim_model_specs(sim_user_input)
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
