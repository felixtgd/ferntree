from pydantic import BaseModel


class FinFormData(BaseModel):
    """Represents financial form data for calculations.

    Attributes:
        model_id (str): The ID of the model.
        electr_price (float): Electricity price in cents/kWh.
        feed_in_tariff (float): Feed-in tariff in cents/kWh.
        pv_price (float): PV system price per kWp.
        battery_price (float): Battery price per kWh.
        useful_life (int): Useful life of the system in years.
        module_deg (float): Annual module degradation rate in percent.
        inflation (float): Annual inflation rate in percent.
        op_cost (float): Annual operation cost as a percentage of investment.
        down_payment (float): Down payment as a percentage of total investment.
        pay_off_rate (float): Annual loan payoff rate.
        interest_rate (float): Annual interest rate on the loan.

    """

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
        """Pydantic model configuration."""

        protected_namespaces = ()


class FinInvestment(BaseModel):
    """Represents the financial investment in the energy system.

    Attributes:
        pv (float): Investment in the PV system.
        battery (float): Investment in the battery system.
        total (float): Total investment.

    """

    pv: float
    battery: float
    total: float


class FinKPIs(BaseModel):
    """Represents financial key performance indicators.

    Attributes:
        investment (FinInvestment): The investment breakdown.
        break_even_year (float): The year when the investment breaks even.
        cum_profit (float): Cumulative profit over the system lifetime.
        cum_cost_savings (float): Cumulative cost savings over the system lifetime.
        cum_feed_in_revenue (float): Cumulative feed-in revenue over system lifetime.
        cum_operation_costs (float): Cumulative operation costs over system lifetime.
        lcoe (float): Levelized cost of electricity.
        solar_interest_rate (float): Effective interest rate of the solar investment.
        loan (float): Initial loan amount.
        loan_paid_off (float): Year when the loan is paid off.

    """

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
    """Represents yearly financial data.

    Attributes:
        year (int): The year of the data.
        cum_profit (float): Cumulative profit up to this year.
        cum_cash_flow (float): Cumulative cash flow up to this year.
        loan (float): Remaining loan balance at the end of this year.

    """

    year: int
    cum_profit: float
    cum_cash_flow: float
    loan: float


class FinResults(BaseModel):
    """Represents the overall financial results.

    Attributes:
        model_id (str): The ID of the model.
        fin_kpis (FinKPIs): The financial key performance indicators.
        yearly_data (list[FinYearlyData]): Yearly fin. data over the system lifetime.

    """

    model_id: str
    fin_kpis: FinKPIs
    yearly_data: list[FinYearlyData]

    class Config:
        """Pydantic model configuration."""

        protected_namespaces = ()
