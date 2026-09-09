"""Define Pydantic models for simulation inputs and results."""

from typing import Optional

from pydantic import BaseModel, Field

from src.db.schemas.energy import EnergyKPIs, PVMonthlyGen
from src.db.schemas.models import SystemSettings


class SimDataIn(BaseModel):
    """Represents input data for a simulation.

    Attributes:
        model_id (str): The ID of the model being simulated.
        run_time (str): The timestamp when the simulation is run.
        T_amb (list[float]): Ambient temperature data.
        G_i (list[float]): Solar irradiance data.
        coordinates (dict[str, str]): Geographical coordinates.
        timezone (str): The timezone of the location.
        timebase (int): The time step of the simulation in seconds.
        planning_horizon (int): The planning horizon for the simulation.
        system_settings (SystemSettings): The energy system settings.

    """

    model_id: str
    run_time: str
    T_amb: list[float]
    G_i: list[float]
    coordinates: dict[str, str]
    timezone: str
    timebase: int
    planning_horizon: int
    system_settings: SystemSettings

    class Config:
        """Pydantic model configuration."""

        protected_namespaces = ()


class SimDataOut(SimDataIn):
    """Represents sim data to be sent out to frontend, extending SimDataIn.

    Additional Attributes:
        sim_id (str): The unique identifier for the simulation.

    """

    sim_id: str


class SimResultsEval(BaseModel):
    """Represents the evaluation results of a simulation.

    Attributes:
        model_id (str): The ID of the model that was simulated.
        energy_kpis (EnergyKPIs): The energy key performance indicators.
        pv_monthly_gen (list[PVMonthlyGen]): Monthly PV generation data.

    """

    model_id: str
    energy_kpis: EnergyKPIs
    pv_monthly_gen: list[PVMonthlyGen]

    class Config:
        """Pydantic model configuration."""

        protected_namespaces = ()


class SimTimestep(BaseModel):
    """Represents a single timestep in the simulation.

    Attributes:
        time (float): The timestamp of the simulation step.
        T_amb (float): Ambient temperature.
        P_solar (float): Solar power.
        P_base (float): Base load power.
        P_pv (float): PV power.
        P_bat (float): Battery power.
        Soc_bat (float): State of charge of the battery.
        fill_level (float): Fill level of the battery.
        P_load_pred (float): Predicted load power.

    """

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
    fill_level: Optional[float] = Field(
        title="Fill Level of Battery",
        description="The fill level of the battery in [0 ... 1]",
        default=None,
    )
    P_load_pred: Optional[float] = Field(
        title="Predicted Net Load of House",
        description="The predicted net load of the house in kW",
        default=None,
    )


class SimTimestepOut(BaseModel):
    """Represents output data for a simulation timestep.

    Attributes:
        time (str): The timestamp of the simulation step.
        Load (float): The load power.
        PV (float): The PV power.
        Battery (float): The battery power.
        Total (float): The total power.
        StateOfCharge (float): The state of charge of the battery.

    """

    time: str
    Load: float
    PV: float
    Battery: float
    Total: float
    StateOfCharge: float
