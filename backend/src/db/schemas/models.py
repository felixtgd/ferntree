from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents a user in the system.

    Attributes:
        user_id (str): The unique identifier for the user.
        name (str): The user's name.
        email (str): The user's email address.
        image (str): URL or path to the user's profile image.
        emailVerified (Optional[str]): Timestamp of when the email was verified,
                                        if applicable.

    """

    user_id: str
    name: str
    email: str
    image: str
    emailVerified: Optional[str]


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
        user_id (str): The ID of the user creating the model.
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

    user_id: str
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

    model_id: str
    sim_id: Optional[str] = None


class Baseload(BaseModel):
    """Represents the baseload for an energy system.

    Attributes:
        annual_consumption (float): Annual electricity consumption in kWh.
        profile_id (int): Identifier for the consumption profile.

    """

    annual_consumption: float
    profile_id: int


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

    time: float
    T_amb: float
    P_solar: float
    P_base: float
    P_pv: float
    P_bat: float
    Soc_bat: float
    fill_level: float
    P_load_pred: float


class StartEndTimes(BaseModel):
    """Represents start and end times for a time range.

    Attributes:
        start_time (str): The start time of the range.
        end_time (str): The end time of the range.

    """

    start_time: str
    end_time: str


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
