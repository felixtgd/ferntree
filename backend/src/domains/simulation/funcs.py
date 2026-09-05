import logging
import subprocess
from datetime import datetime
from subprocess import CompletedProcess
from typing import Any

from src.db.schemas import (
    PV,
    Baseload,
    Battery,
    BatteryCtrl,
    ModelDataOut,
    SimDataIn,
    SystemSettings,
)
from src.domains.solar import geolocator, pvgis_api

logger: logging.Logger = logging.getLogger("ferntree")


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
        "src/domains/ferntree/ferntree.py",
        "--sim_id",
        sim_id,
        "--model_id",
        model_id,
    ]

    logger.info(f"Running Ferntree simulation with command: {command}")
    completed_process: CompletedProcess[Any] = subprocess.run(command)

    # Check if the simulation has finished successfully
    if completed_process.returncode != 0:
        raise RuntimeError(
            f"Ferntree Simulation failed. Return code: {completed_process.returncode}"
        )

    return True
