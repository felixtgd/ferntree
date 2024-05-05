from pydantic import BaseModel, Field


class TimestepData(BaseModel):
    time: float = Field(
        title="Time", description="The timestamp in seconds", optional=False
    )
    T_amb: float = Field(
        title="Ambient Temperature",
        description="The ambient temperature in degree Celsius",
        optional=False,
    )
    P_solar: float = Field(
        title="Solar Irradiance",
        description="The solar irradiance in W/m2",
        optional=False,
    )
    P_base: float = Field(
        title="Baseload Power", description="The baseload power in kW", optional=False
    )
    P_pv: float = Field(
        title="PV Power Generation",
        description="The PV power generation in kW",
        optional=False,
    )
    P_bat: float = Field(
        title="Battery Power", description="The battery power in kW", optional=False
    )
    Soc_bat: float = Field(
        title="State of Charge of Battery",
        description="The state of charge of the battery in kWh",
        optional=False,
    )
    fill_level: float = Field(
        title="Fill Level of Battery",
        description="The fill level of the battery in [0 ... 1]",
        optional=True,
    )
    P_load_pred: float = Field(
        title="Predicted Net Load of House",
        description="The predicted net load of the house in kW",
        optional=True,
    )
