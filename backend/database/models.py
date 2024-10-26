from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str
    name: str
    email: str
    image: str
    emailVerified: Optional[str]


class ModelDataIn(BaseModel):
    user_id: str
    model_name: str
    location: str
    roof_incl: int
    roof_azimuth: int
    electr_cons: float
    peak_power: float
    battery_cap: float

    class Config:
        protected_namespaces = ()


class ModelDataOut(ModelDataIn):
    model_id: str
    sim_id: Optional[str] = None


class Baseload(BaseModel):
    annual_consumption: float
    profile_id: int


class PV(BaseModel):
    roof_tilt: int
    roof_azimuth: int
    peak_power: float


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
    capacity: float
    max_power: float
    soc_init: float
    battery_ctrl: BatteryCtrl


class SystemSettings(BaseModel):
    baseload: Baseload
    pv: PV
    battery: Battery


class SimDataIn(BaseModel):
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
        protected_namespaces = ()


class SimDataOut(SimDataIn):
    sim_id: str


class EnergyKPIs(BaseModel):
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
    month: str
    pv_generation: float


class SimResultsEval(BaseModel):
    model_id: str
    energy_kpis: EnergyKPIs
    pv_monthly_gen: list[PVMonthlyGen]

    class Config:
        protected_namespaces = ()


class SimTimestep(BaseModel):
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
    start_time: str
    end_time: str


class SimTimestepOut(BaseModel):
    time: str
    Load: float
    PV: float
    Battery: float
    Total: float
    StateOfCharge: float


class FinFormData(BaseModel):
    model_id: str
    electr_price: float
    feed_in_tariff: float
    pv_price: float
    battery_price: float
    useful_life: int
    module_deg: float
    inflation: float
    op_cost: float
    down_payment: float
    pay_off_rate: float
    interest_rate: float

    class Config:
        protected_namespaces = ()


class FinInvestment(BaseModel):
    pv: float
    battery: float
    total: float


class FinKPIs(BaseModel):
    investment: FinInvestment
    break_even_year: float
    cum_profit: float
    cum_cost_savings: float
    cum_feed_in_revenue: float
    cum_operation_costs: float
    lcoe: float
    solar_interest_rate: float
    loan: float
    loan_paid_off: float


class FinYearlyData(BaseModel):
    year: int
    cum_profit: float
    cum_cash_flow: float
    loan: float


class FinResults(BaseModel):
    model_id: str
    fin_kpis: FinKPIs
    yearly_data: list[FinYearlyData]

    class Config:
        protected_namespaces = ()
