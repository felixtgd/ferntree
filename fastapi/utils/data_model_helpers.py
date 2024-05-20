from database.models import (
    SimUserInputForm,
    SimParams,
    Baseload,
    PV,
    BatteryCtrl,
    Battery,
    House,
    SimModelSpecs,
)


async def define_sim_model_specs(
    sim_user_input: SimUserInputForm, coordinates: dict, timezone: str
) -> SimModelSpecs:
    """Defines the simulation model specifications based on user input.
    Uses default values for some specs.

    Args:
        sim_user_input (SimUserInputForm): The user input form.
        coordinates (dict): Dictionary with lat and lon coordinates.
        timezone (str): The timezone string.

    Returns:
        SimModelSpecs: The simulation model specifications. Will be written
        to database as a document.

    """

    sim_params = SimParams(
        timebase=3600,
        timezone=timezone if timezone else "UTC",
        planning_horizon=1,
        location=sim_user_input.location,
        coordinates=coordinates,
    )

    baseload = Baseload(
        annual_consumption=sim_user_input.electr_cons,
        profile_id=1,  # TODO: Find better way to set profile_id
    )

    pv = PV(
        roof_tilt=sim_user_input.roof_incl,
        roof_azimuth=sim_user_input.roof_azimuth,
        peak_power=sim_user_input.peak_power,
    )

    battery_ctrl = BatteryCtrl(
        planning_horizon=1,
        useable_capacity=0.8,
        greedy=True,
        opt_fill=False,
    )

    battery = Battery(
        capacity=sim_user_input.battery_cap,
        max_power=sim_user_input.battery_cap,  # TODO: Add max_power to user input?
        soc_init=0.0,
        battery_ctrl=battery_ctrl,
    )

    house = House(
        baseload=baseload,
        pv=pv,
        battery=battery,
    )

    sim_model_specs = SimModelSpecs(
        sim_params=sim_params,
        house=house,
    )

    return sim_model_specs
