from pydantic import BaseModel, Field


class TimestepData(BaseModel):
    """The data model for a single timestep of the simulation."""

    time: float = Field(title="Time", description="The timestamp in seconds")
    T_amb: float = Field(
        title="Ambient Temperature",
        description="The ambient temperature in degree Celsius",
    )
    P_solar: float = Field(
        title="Solar Irradiance", description="The solar irradiance in W/m2"
    )
    P_base: float = Field(
        title="Baseload Power", description="The baseload power in kW"
    )
    P_pv: float = Field(
        title="PV Power Generation", description="The PV power generation in kW"
    )
    P_bat: float = Field(title="Battery Power", description="The battery power in kW")
    Soc_bat: float = Field(
        title="State of Charge of Battery",
        description="The state of charge of the battery in kWh",
    )
    fill_level: float = Field(
        title="Fill Level of Battery",
        description="The fill level of the battery in [0 ... 1]",
        default=None,
    )
    P_load_pred: float = Field(
        title="Predicted Net Load of House",
        description="The predicted net load of the house in kW",
        default=None,
    )


class LoadProfile(BaseModel):
    """The data model for the load profile of the house."""

    type: str = Field(
        title="Type",
        description="Default: normalised annual loadprofile",
    )
    profile_id: int = Field(
        title="Profile ID",
        description="The ID of the load profile",
    )
    load_profile: list[float] = Field(
        title="Load Profile",
        description="The load profile in kW",
    )
