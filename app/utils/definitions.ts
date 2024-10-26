import { z } from "zod";


// FORM STATE for messages and errors in form submission
export type FormState = {
  errors?: Record<string, string[]>;
  message?: string | null;
  model_id?: string | null;
  timestamp?: string | null;
};

export type CoordinateData = {
  lat: string;
  lon: string;
  display_name: string;
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
  sim_id?: string;
  model_id?: string;
  coordinates?: CoordinateData;
  time_created?: string;
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

// SIMULATION RESULTS MODELS for /workspace/simulations
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
  labels: { center: number; title: number; };
  title: string;
}

export type SimTimestep = {
  time: string;
  Load: number;
  PV: number;
  Battery: number;
  Total: number;
  StateOfCharge: number;
};

// FINANCES
// MODEL DATA for /workspace/models
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

export const FinDataSchema = z.object({
  model_id: z.string(),
  electr_price: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0 ct/kWh' })
      .lte(1000, { message: 'Must be at most 1000 ct/kWh' }),
  feed_in_tariff: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0 ct/kWh' })
      .lte(1000, { message: 'Must be at most 1000 ct/kWh' }),
  pv_price: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0 €/kWp' })
      .lte(10000, { message: 'Must be at most 10,000 €/kWp' }),
  battery_price: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0 €/kWh' })
      .lte(10000, { message: 'Must be at most 10,000 €/kWh' }),
  useful_life: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0 years' })
      .lte(50, { message: 'Must be at most 50 years' }),
  module_deg: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0%' })
      .lt(100, { message: 'Must be less than 100%' }),
  inflation: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0%' })
      .lte(100, { message: 'Must be at most 100%' }),
  op_cost: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0%' })
      .lte(100, { message: 'Must be at most 100%' }),
  down_payment: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0%' })
      .lte(100, { message: 'Must be at most 100%' }),
  pay_off_rate: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0%' })
      .lte(100, { message: 'Must be at most 100%' }),
  interest_rate: z.coerce
      .number()
      .gt(0, { message: 'Must be greater than 0%' })
      .lte(100, { message: 'Must be at most 100%' }),
});


export type FinInvestment = {
  pv: number;
  battery: number;
  total: number;
}

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
}

export type FinYearlyData = {
  year: number;
  cum_profit: number;
  cum_cash_flow: number;
  loan: number;
}

export type FinChartData = {
  "Year": number;
  "Cum. Profit": number;
  "Investment": number;
  "Cum. Cash Flow": number;
  "Loan": number;
};

export type FinResults = {
  model_id: string;
  fin_kpis: FinKPIs;
  yearly_data: FinYearlyData[];
}

export type FinBarChartItem = {
  type: string;
  'PV'?: number;
  'Battery'?: number;
  'Cost savings'?: number;
  'Feed-in revenue'?: number;
  'Operation costs'?: number;
};

export type EmailFormData = {
  name?: string;
  email?: string;
  category: string;
  message: string;
};

export const EmailDataSchema = z.object({
  name: z.string()
    .min(1, { message: 'Please specify a name' })
    .max(100, { message: 'Name must be at most 100 characters long' }),
  email: z.string()
    .email({ message: 'Please enter a valid email address' })
    .max(100, { message: 'Email must be at most 100 characters long' }),
  category: z.string()
    .max(100, { message: 'Category must be at most 100 characters long' })
    .min(1, { message: 'Please specify a category' }),
  message: z.string()
    .max(1000, { message: 'Message must be at most 1000 characters long' })
    .min(1, { message: 'Please specify a message' }),
});
