from pydantic import BaseModel, Field


# User input for simulation
class SimUserInputForm(BaseModel):
    location: str = Field(
        title="Location", description="The location of the simulation"
    )
    electr_cons: float = Field(
        title="Electricity Consumption",
        description="The electricity consumption in kWh",
    )
    roof_incl: int = Field(
        title="Roof Inclination", description="The inclination of the roof in degrees"
    )
    roof_azimuth: int = Field(
        title="Roof Azimuth", description="The azimuth of the roof in degrees"
    )
    peak_power: float = Field(
        title="Peak Power", description="The peak power of the PV system in kWp"
    )
    battery_cap: float = Field(
        title="Battery Capacity", description="The capacity of the battery in kWh"
    )
    electr_price: float = Field(
        title="Electricity Price", description="The price of electricity in €/kWh"
    )
    down_payment: float = Field(
        title="Down Payment", description="The down payment in €"
    )
    pay_off_rate: float = Field(
        title="Pay Off Rate", description="The pay off rate in €/kWh"
    )
    interest_rate: float = Field(
        title="Interest Rate", description="The interest rate in %"
    )


# Data model for solar irradiance data queried from PVGIS
class PvgisInputData(BaseModel):
    time: str = Field(title="Time", description="The timestamp of the data point")
    G_i: float = Field(
        title="Solar Irradiance",
        description="Global irradiance on the inclined plane (plane of the array): G(i) in [W/m2]",
    )
    T2m: float = Field(
        title="Temperature", description="2-m air temperature: T2m in [degree Celsius]"
    )


# MongoDB: Document model for collection "simulation_coll"
class SimTimeSeriesDoc(BaseModel):
    user_id: int = Field(title="User ID", description="The ID of the user")
    created_at: str = Field(
        title="Created At", description="The timestamp of the simulation"
    )
    T_amb: list[float] = Field(
        title="Ambient Temperature",
        description="The ambient temperature in degree Celsius",
    )
    G_i: list[float] = Field(
        title="Solar Irradiance",
        description="The solar irradiance in W/m2",
    )
    # timeseries_data: list[PvgisInputData] = Field(
    #     title="Timeseries Data", description="Timeseries data of the simulation"
    # )


class SimParams(BaseModel):
    timebase: int = Field(
        default=3600, title="Timebase", description="The timebase in seconds"
    )
    timezone: str = Field(
        default="UTC", title="Timezone", description="The timezone of the simulation"
    )
    planning_horizon: int = Field(
        default=1, title="Planning Horizon", description="The planning horizon in days"
    )
    location: str = Field(
        title="Location", description="The location of the simulation"
    )
    coordinates: dict = Field(
        title="Coordinates", description="The coordinates of the location"
    )


class Baseload(BaseModel):
    annual_consumption: float = Field(
        title="Annual Consumption", description="The annual consumption in kWh"
    )
    profile_id: int = Field(
        title="Profile ID", description="The profile ID of the baseload profile"
    )


class PV(BaseModel):
    roof_tilt: int = Field(
        title="Roof Tilt", description="The tilt of the roof in degrees"
    )
    roof_azimuth: int = Field(
        title="Roof Azimuth", description="The azimuth of the roof in degrees"
    )
    peak_power: float = Field(
        title="Peak Power", description="The peak power of the PV system in kWp"
    )


class BatteryCtrl(BaseModel):
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
    capacity: float = Field(
        title="Capacity", description="The capacity of the battery in kWh"
    )
    max_power: float = Field(
        title="Max Power", description="The maximum power of the battery in kW"
    )
    soc_init: float = Field(
        title="Initial SOC",
        description="The initial state of charge of the battery in kWh",
    )
    battery_ctrl: BatteryCtrl = Field(
        title="Battery Control", description="The battery control"
    )


class House(BaseModel):
    baseload: Baseload = Field(title="Baseload", description="The baseload settings")
    pv: PV = Field(title="PV", description="The PV settings")
    battery: Battery = Field(title="Battery", description="The battery settings")


class SimModelSpecs(BaseModel):
    sim_params: SimParams = Field(
        title="Simulation Parameters", description="The simulation parameters"
    )
    house: House = Field(title="House", description="The house settings")


class SimModelSpecsDoc(BaseModel):
    user_id: int = Field(title="User ID", description="The ID of the user")
    sim_id: str = Field(title="Simulation ID", description="The ID of the simulation")
    created_at: str = Field(
        title="Created At", description="The timestamp of the simulation"
    )
    sim_model_specs: SimModelSpecs = Field(
        title="Simulation Model Specifications",
        description="The simulation model specifications",
    )
