// Vite dev-server plugin that serves all /api/mock/* routes locally.
// No external backend process is needed during development.
//
// Usage: imported by vite.config.ts and added to the `plugins` array.

import type { Plugin, Connect } from 'vite';
import type { ServerResponse } from 'http';

// ---------------------------------------------------------------------------
// Static mock data
// ---------------------------------------------------------------------------

const MODELS = [
  {
    model_id: 'mock-model-1',
    model_name: 'Mock Home',
    location: 'Berlin, Germany',
    roof_incl: 30,
    roof_azimuth: 0,
    electr_cons: 4000,
    peak_power: 10,
    battery_cap: 10,
    sim_id: 'mock-sim-1',
  },
  {
    model_id: 'mock-model-2',
    model_name: 'Mock Flat',
    location: 'Munich, Germany',
    roof_incl: 45,
    roof_azimuth: 45,
    electr_cons: 2500,
    peak_power: 6,
    battery_cap: 5,
    sim_id: null,
  },
];

const SIM_RESULTS = {
  model_id: 'mock-model-1',
  energy_kpis: {
    annual_consumption: 4000,
    pv_generation: 9500,
    grid_consumption: 1200,
    grid_feed_in: 6700,
    self_consumption: 2800,
    self_consumption_rate: 0.29,
    self_sufficiency: 0.70,
  },
  pv_monthly_gen: [
    { month: 'Jan', pv_generation: 300 },
    { month: 'Feb', pv_generation: 450 },
    { month: 'Mar', pv_generation: 750 },
    { month: 'Apr', pv_generation: 900 },
    { month: 'May', pv_generation: 1100 },
    { month: 'Jun', pv_generation: 1200 },
    { month: 'Jul', pv_generation: 1150 },
    { month: 'Aug', pv_generation: 1050 },
    { month: 'Sep', pv_generation: 800 },
    { month: 'Oct', pv_generation: 500 },
    { month: 'Nov', pv_generation: 350 },
    { month: 'Dec', pv_generation: 250 },
  ],
};

function buildTimeseries() {
  const base = new Date('2023-06-19T08:00:00Z');
  return Array.from({ length: 24 }, (_, i) => {
    const t = new Date(base.getTime() + i * 3600 * 1000);
    const pv = i >= 6 && i <= 18 ? Math.round(2 + Math.sin(((i - 6) / 12) * Math.PI) * 5) : 0;
    const load = 1.5;
    const battery = pv > load ? Math.min(pv - load, 2) : 0;
    const total = load - pv - battery;
    return {
      time: t.toISOString(),
      Load: load,
      PV: pv,
      Battery: battery,
      Total: Math.round(total * 10) / 10,
      StateOfCharge: Math.min(100, Math.round(40 + i * 2)),
    };
  });
}

const INVESTMENT_TOTAL = 15000 + 6500;
const YEARLY_DATA = Array.from({ length: 21 }, (_, i) => ({
  year: i,
  cum_profit: Math.round(-INVESTMENT_TOTAL + i * 2100),
  cum_cash_flow: Math.round(-INVESTMENT_TOTAL * 0.75 + i * 2100),
  loan: Math.max(0, Math.round(INVESTMENT_TOTAL * 0.75 - i * 2100 * 0.5)),
}));

const FIN_RESULTS = {
  model_id: 'mock-model-1',
  fin_kpis: {
    investment: { pv: 15000, battery: 6500, total: INVESTMENT_TOTAL },
    break_even_year: 10.2,
    cum_profit: 17000,
    cum_cost_savings: 28000,
    cum_feed_in_revenue: 8500,
    cum_operation_costs: 2150,
    lcoe: 8.5,
    solar_interest_rate: 7.2,
    loan: 16125,
    loan_paid_off: 8.5,
  },
  yearly_data: YEARLY_DATA,
};

const FIN_FORM_DATA = [
  {
    model_id: 'mock-model-1',
    electr_price: 45,
    feed_in_tariff: 8,
    pv_price: 1500,
    battery_price: 650,
    useful_life: 20,
    module_deg: 0.5,
    inflation: 3,
    op_cost: 1,
    down_payment: 25,
    pay_off_rate: 10,
    interest_rate: 5,
  },
];

// ---------------------------------------------------------------------------
// Helper: send JSON response
// ---------------------------------------------------------------------------
function json(res: ServerResponse, data: unknown, status = 200): void {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body),
    'Access-Control-Allow-Origin': '*',
  });
  res.end(body);
}

// ---------------------------------------------------------------------------
// Plugin
// ---------------------------------------------------------------------------
export function mockApiPlugin(): Plugin {
  return {
    name: 'mock-api',
    configureServer(server) {
      server.middlewares.use((req: Connect.IncomingMessage, res: ServerResponse, next) => {
        const url = req.url ?? '';
        const path = url.split('?')[0];

        // Only handle /api/mock/* routes
        if (!path.startsWith('/api/mock/')) {
          next();
          return;
        }

        const route = path.replace('/api/mock', '');
        const method = req.method ?? 'GET';

        // OPTIONS preflight
        if (method === 'OPTIONS') {
          res.writeHead(204, { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': '*', 'Access-Control-Allow-Headers': '*' });
          res.end();
          return;
        }

        // GET /workspace/models/fetch-models
        if (method === 'GET' && route === '/workspace/models/fetch-models') {
          json(res, MODELS);
          return;
        }

        // POST /workspace/models/submit-model
        if (method === 'POST' && route === '/workspace/models/submit-model') {
          json(res, 'mock-model-new');
          return;
        }

        // DELETE /workspace/models/delete-model
        if (method === 'DELETE' && route === '/workspace/models/delete-model') {
          json(res, true);
          return;
        }

        // GET /workspace/simulations/run-sim
        if (method === 'GET' && route === '/workspace/simulations/run-sim') {
          json(res, { run_successful: true });
          return;
        }

        // GET /workspace/simulations/fetch-sim-results
        if (method === 'GET' && route === '/workspace/simulations/fetch-sim-results') {
          json(res, SIM_RESULTS);
          return;
        }

        // POST /workspace/simulations/fetch-sim-timeseries
        if (method === 'POST' && route === '/workspace/simulations/fetch-sim-timeseries') {
          json(res, buildTimeseries());
          return;
        }

        // GET /workspace/finances/fetch-fin-form-data
        if (method === 'GET' && route === '/workspace/finances/fetch-fin-form-data') {
          json(res, FIN_FORM_DATA);
          return;
        }

        // POST /workspace/finances/submit-fin-form-data
        if (method === 'POST' && route === '/workspace/finances/submit-fin-form-data') {
          json(res, 'mock-model-1');
          return;
        }

        // GET /workspace/finances/fetch-fin-results
        if (method === 'GET' && route === '/workspace/finances/fetch-fin-results') {
          json(res, FIN_RESULTS);
          return;
        }

        // Unknown /api/mock/* route
        json(res, { error: `No mock handler for ${method} ${route}` }, 404);
      });
    },
  };
}
