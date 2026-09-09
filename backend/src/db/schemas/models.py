from typing import Optional

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Represents geographical coordinates and location information.

    Attributes:
        lat (str): The latitude of the location.
        lon (str): The longitude of the location.
        display_name (str): A human-readable name for the location.

    """

    lat: str
    lon: str
    display_name: str


class ModelDataIn(BaseModel):
    """Represents input data for creating a new model.

    Attributes:
        user_id (Optional[int]): The ID of the user creating the model.
        model_name (str): The name of the model.
        location (str): The location for the model.
        roof_incl (int): The roof inclination in degrees.
        roof_azimuth (int): The roof azimuth in degrees.
        electr_cons (float): Annual electricity consumption in kWh.
        peak_power (float): Peak power of the PV system in kWp.
        battery_cap (float): Battery capacity in kWh.
        coordinates (Optional[Coordinates]): Geographical coordinates of the location.
        time_created (Optional[str]): Timestamp of when the model was created.

    """

    user_id: Optional[int] = None
    model_name: str
    location: str
    roof_incl: int
    roof_azimuth: int
    electr_cons: float
    peak_power: float
    battery_cap: float
    coordinates: Optional[Coordinates] = None
    time_created: Optional[str] = None

    class Config:
        """Pydantic model configuration."""

        protected_namespaces = ()


class ModelDataOut(ModelDataIn):
    """Represents model data to send out to frontend, extending ModelDataIn.

    Additional Attributes:
        model_id (str): The unique identifier for the model.
        sim_id (Optional[str]): The ID of the associated simulation, if any.

    """

    user_id: int
    model_id: str
    sim_id: Optional[str] = None


class Baseload(BaseModel):
    """Represents the baseload for an energy system.

    Attributes:
        annual_consumption (float): Annual electricity consumption in kWh.

    """

    annual_consumption: float


class PV(BaseModel):
    """Represents a photovoltaic system.

    Attributes:
        roof_tilt (int): The tilt angle of the roof in degrees.
        roof_azimuth (int): The azimuth angle of the roof in degrees.
        peak_power (float): The peak power of the PV system in kWp.

    """

    roof_tilt: int
    roof_azimuth: int
    peak_power: float


class BatteryCtrl(BaseModel):
    """Represents the control parameters for a battery system.

    Attributes:
        planning_horizon (int): The planning horizon in days.
        useable_capacity (float): The useable capacity of the battery
                                    as a fraction [0 ... 1].
        greedy (bool): Whether to use greedy optimization.
        opt_fill (bool): Whether to optimize the fill level of the battery.

    """

    planning_horizon: int = Field(
        default=1, title="Planning Horizon", description="The planning horizon in days"
    )
    useable_capacity: float = Field(
        title="Useable Capacity",
        description="The useable capacity of the battery in [0 ... 1]",
    )
    greedy: bool = Field(
        default=True, title="Greedy", description="Use greedy optimization"
    )
    opt_fill: bool = Field(
        default=False,
        title="Optimal Fill",
        description="Optimize the fill level of the battery",
    )


class Battery(BaseModel):
    """Represents a battery system.

    Attributes:
        capacity (float): The total capacity of the battery in kWh.
        max_power (float): The maximum power output of the battery in kW.
        soc_init (float): The initial state of charge of the battery.
        battery_ctrl (BatteryCtrl): The control parameters for the battery.

    """

    capacity: float
    max_power: float
    soc_init: float
    battery_ctrl: BatteryCtrl


class SystemSettings(BaseModel):
    """Represents the overall settings for an energy system.

    Attributes:
        baseload (Baseload): The baseload settings.
        pv (PV): The photovoltaic system settings.
        battery (Battery): The battery system settings.

    """

    baseload: Baseload
    pv: PV
    battery: Battery
