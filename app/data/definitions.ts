// This file contains type definitions for your data.
// It describes the shape of the data, and what data type each property should accept.
// For simplicity of teaching, we're manually defining these types.
// However, these types are generated automatically if you're using an ORM such as Prisma.

export type SimulationModel = {
  location: string;
  electr_cons: number;
  roof_incl: number;
  roof_azimuth: number;
  peak_power: number;
  battery_cap: number;
  electr_price: number;
  down_payment: number;
  pay_off_rate: number;
  interest_rate: number;
};

export type PvData = {
  status: string;
  // model: SimulationModel;
  total_investment: number;
  break_even_year: number;
};


export type SimModelSummary = {
  electr_cons: number;
  pv_power: number;
  battery_capacity: number;
  electr_price: number;
  down_payment: number;
  pay_off_rate: number;
  interest_rate: number;
};

export type SimEnergyKPIs = {
  baseload_demand: number;
  pv_generation: number;
  grid_consumption: number;
  grid_feed_in: number;
  self_consumption: number;
  self_consumption_rate: number;
  self_sufficiency: number;
};

export type SimFinancialAssumptions = {
  price_increase: number;
  pv_costs_per_kWp: number;
  battery_costs_per_kWh: number;
  module_degradation: number;
  operation_costs: number;
  feed_in_tariff: number;
};

export type SimFinancialInvestment = {
  pv: number;
  battery: number;
  total: number;
};

export type SimFinancialKPIs = {
  investment: SimFinancialInvestment;
  break_even_year: number;
  cum_profit_25yrs: number;
  cum_cost_savings_25yrs: number;
  cum_feed_in_revenue_25yrs: number;
  cum_operation_costs_25yrs: number;
  lcoe: number;
  solar_interest_rate: number;
};

export type SimFinancialAnalysis = {
  assumptions: SimFinancialAssumptions;
  kpis: SimFinancialKPIs;
};

export type SimEvaluation = {
  sim_id: string;
  sim_model_summary: SimModelSummary;
  energy_kpis: SimEnergyKPIs;
  financial_analysis: SimFinancialAnalysis;
};

export type DonutChartData = {
  data: { name: string; value: number; share: number; }[];
  labels: { center: number; title: number; };
  title: string;
}

export type PVMonthlyGenData = {
  month: string;
  PVGeneration: number;
};

export type FinBarChartItem = {
  type: string;
  'PV'?: number;
  'Battery'?: number;
  'Cost savings'?: number;
  'Feed-in revenue'?: number;
  'Operation costs'?: number;
};

export type PowerTimeseriesItem = {
  time: string;
  Load: number;
  PV: number;
  Battery: number;
  Total: number;
  StateOfCharge: number;
};

export type ModelSummary = {
  location: string;
  electr_cons: number;
  roof_incl: number;
  roof_azimuth: number;
  peak_power: number;
  battery_cap: number;
};
