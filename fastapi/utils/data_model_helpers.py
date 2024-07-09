from database.models import (
    UserInputForm,
    SimParams,
    Baseload,
    PV,
    BatteryCtrl,
    Battery,
    House,
    Finance,
    ModelSpecs,
    FilteredTimeseriesData,
    FormattedTimeseriesData,
)

from datetime import datetime


async def define_model_specs(
    user_input: UserInputForm, coordinates: dict, timezone: str
) -> ModelSpecs:
    """Defines the simulation model specifications based on user input.
    Uses default values for some specs.

    Args:
        sim_user_input (UserInputForm): The user input form.
        coordinates (dict): Dictionary with lat and lon coordinates.
        timezone (str): The timezone string.

    Returns:
        ModelSpecs: The model specifications. Will be written
        to database as a document.

    """

    sim_params = SimParams(
        timebase=3600,
        timezone=timezone if timezone else "UTC",
        planning_horizon=1,
        location=user_input.location,
        coordinates=coordinates,
    )

    baseload = Baseload(
        annual_consumption=user_input.electr_cons,
        profile_id=1,  # TODO: Find better way to set profile_id
    )

    pv = PV(
        roof_tilt=user_input.roof_incl,
        roof_azimuth=user_input.roof_azimuth,
        peak_power=user_input.peak_power,
    )

    battery_ctrl = BatteryCtrl(
        planning_horizon=1,
        useable_capacity=0.8,
        greedy=True,
        opt_fill=False,
    )

    battery = Battery(
        capacity=user_input.battery_cap,
        max_power=user_input.battery_cap,  # TODO: Add max_power to user input?
        soc_init=0.0,
        battery_ctrl=battery_ctrl,
    )

    house = House(
        baseload=baseload,
        pv=pv,
        battery=battery,
    )

    finance = Finance(
        electr_price=user_input.electr_price,
        down_payment=user_input.down_payment,
        pay_off_rate=user_input.pay_off_rate,
        interest_rate=user_input.interest_rate,
    )

    model_specs = ModelSpecs(
        sim_params=sim_params,
        house=house,
        finance=finance,
    )

    return model_specs


def format_timeseries_data(
    timeseries_data: list[FilteredTimeseriesData],
) -> list[FormattedTimeseriesData]:
    """Formats the timeseries data for the frontend.

    Args:
        timeseries_data (list[FilteredTimeseriesData]): The timeseries data of simulation results.

    Returns:
        list[FormattedTimeseriesData]: The formatted timeseries data.

    """
    return [
        FormattedTimeseriesData(
            time=datetime.fromtimestamp(data.time).strftime("%d-%m-%Y %H:%M"),
            Load=data.P_base,
            PV=data.P_pv,
            Battery=data.P_bat,
            Total=data.P_base + data.P_pv + data.P_bat,
            StateOfCharge=data.Soc_bat,
        )
        for data in timeseries_data
    ]
