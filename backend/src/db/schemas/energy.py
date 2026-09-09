from pydantic import BaseModel, Field


class EnergyKPIs(BaseModel):
    """Represents key performance indicators for energy consumption and production.

    Attributes:
        annual_consumption (float): Annual electricity consumption in kWh.
        pv_generation (float): Annual PV generation in kWh.
        grid_consumption (float): Annual grid consumption in kWh.
        grid_feed_in (float): Annual grid feed-in in kWh.
        self_consumption (float): Annual self-consumption in kWh.
        self_consumption_rate (float): Annual self-consumption rate.
        self_sufficiency (float): Annual self-sufficiency rate.

    """

    annual_consumption: float = Field(
        title="Annual electr. consumption",
        description="The annual electricity consumption in kWh",
    )
    pv_generation: float = Field(
        title="PV Generation",
        description="The annual PV generation in kWh",
    )
    grid_consumption: float = Field(
        title="Grid Consumption",
        description="The annual grid consumption in kWh",
    )
    grid_feed_in: float = Field(
        title="Grid Feed-in",
        description="The annual grid feed-in in kWh",
    )
    self_consumption: float = Field(
        title="Self Consumption",
        description="The annual self consumption in kWh",
    )
    self_consumption_rate: float = Field(
        title="Self Consumption Rate",
        description="The annual self consumption rate",
    )
    self_sufficiency: float = Field(
        title="Self Sufficiency",
        description="The annual self sufficiency",
    )


class PVMonthlyGen(BaseModel):
    """Represents monthly PV generation data.

    Attributes:
        month (str): The name of the month.
        pv_generation (float): The PV generation for the month in kWh.

    """

    month: str
    pv_generation: float
