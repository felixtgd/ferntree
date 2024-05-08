from datetime import datetime
import os
import subprocess

from database.models import (
    SimUserInputForm,
    SimTimeSeriesDoc,
    SimModelSpecsDoc,
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
