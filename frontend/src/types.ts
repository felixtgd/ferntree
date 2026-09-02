// TypeScript types ported from frontend/app/utils/definitions.ts
// Omitted: FormState, EmailFormData (not needed in vanilla app)

export type CoordinateData = {
  lat: string;
  lon: string;
  display_name: string;
};

export type ModelData = {
  model_name: string;
  location: string;
  roof_incl: number;
  roof_azimuth: number;
  electr_cons: number;
  peak_power: number;
  battery_cap: number;
  sim_id?: string;
  model_id?: string;
  coordinates?: CoordinateData;
  time_created?: string;
};

export type EnergyKPIs = {
  annual_consumption: number;
  pv_generation: number;
  grid_consumption: number;
  grid_feed_in: number;
  self_consumption: number;
  self_consumption_rate: number;
  self_sufficiency: number;
};

export type PVMonthlyGen = {
  month: string;
  pv_generation: number;
};

export type SimResultsEval = {
  model_id: string;
  energy_kpis: EnergyKPIs;
  pv_monthly_gen: PVMonthlyGen[];
};

export type DonutChartData = {
  data: { name: string; value: number; share: number; tooltip: string }[];
  labels: { center: number; title: number };
  title: string;
};

export type SimTimestep = {
  time: string;
  Load: number;
  PV: number;
  Battery: number;
  Total: number;
  StateOfCharge: number;
};

export type FinData = {
  model_id: string;
  electr_price: number;
  feed_in_tariff: number;
  pv_price: number;
  battery_price: number;
  useful_life: number;
  module_deg: number;
  inflation: number;
  op_cost: number;
  down_payment: number;
  pay_off_rate: number;
  interest_rate: number;
};

export type FinInvestment = {
  pv: number;
  battery: number;
  total: number;
};

export type FinKPIs = {
  investment: FinInvestment;
  break_even_year: number;
  cum_profit: number;
  cum_cost_savings: number;
  cum_feed_in_revenue: number;
  cum_operation_costs: number;
  lcoe: number;
  solar_interest_rate: number;
  loan: number;
  loan_paid_off: number;
};

export type FinYearlyData = {
  year: number;
  cum_profit: number;
  cum_cash_flow: number;
  loan: number;
};

export type FinChartData = {
  Year: number;
  'Cum. Profit'?: number;
  Investment?: number;
  'Cum. Cash Flow'?: number;
  Loan?: number;
};

export type FinResults = {
  model_id: string;
  fin_kpis: FinKPIs;
  yearly_data: FinYearlyData[];
};

export type FinBarChartItem = {
  type: string;
  PV?: number;
  Battery?: number;
  'Cost savings'?: number;
  'Feed-in revenue'?: number;
  'Operation costs'?: number;
};
