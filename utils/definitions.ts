import { z } from "zod";


// FORM STATE for messages and errors in form submission
export type FormState = {
  errors?: Record<string, string[]>;
  message?: string | null;
};

// MODEL DATA for /workspace/models
export type ModelData = {
  model_name: string;
  location: string;
  roof_incl: number;
  roof_azimuth: number;
  electr_cons: number;
  peak_power: number;
  battery_cap: number;
};

export const ModelDataSchema = z.object({
  model_name: z.string()
      .max(100, { message: 'Model name must be at most 100 characters long' })
      .min(1, { message: 'Please specify a model name' }),
  location: z.string()
      .max(100, { message: 'Location must be at most 100 characters long' })
      .min(1, { message: 'Please specify a location' }),
  roof_incl: z.coerce
      .number()
      .gte(0, { message: 'Must be at least 0°' })
      .lte(90, { message: 'Must be at most 90°' }),
  roof_azimuth: z.coerce
      .number()
      .gte(-180, { message: 'Must be at least -180°' })
      .lte(180, { message: 'Must be at most 180°' }),
  electr_cons: z.coerce
      .number()
      .gte(0, { message: 'Must be at least 0 kWh' })
      .lte(100000, { message: 'Must be at most 100,000 kWh' }),
  peak_power: z.coerce
      .number()
      .gte(0, { message: 'Must be at least 0 kWp' })
      .lte(100000, { message: 'Must be at most 100,000 kWp' }),
  battery_cap: z.coerce
      .number()
      .gte(0, { message: 'Must be at least 0 kWh' })
      .lte(100000, { message: 'Must be at most 100,000 kWh' }),
});















// ------------- OLD SHIT --------------------

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
