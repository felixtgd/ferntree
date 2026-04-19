// Finances page — handles both /workspace/finances and
// /workspace/finances/:model_id

import {
  Chart,
  BarElement,
  BarController,
  LineElement,
  LineController,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';
import { z } from 'zod';
import { fetchModels, fetchFinFormData, submitFinFormData, fetchFinResults } from '../api';
import { navigate } from '../router';
import { showLoadingOverlay, hideLoadingOverlay } from '../overlay';
import type { ModelData, FinData, FinKPIs, FinResults, FinYearlyData } from '../types';

Chart.register(
  BarElement,
  BarController,
  LineElement,
  LineController,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
);

// ---------------------------------------------------------------------------
// Listener lifecycle
// ---------------------------------------------------------------------------
let listenerController: AbortController | null = null;

// ---------------------------------------------------------------------------
// Chart instance holders
// ---------------------------------------------------------------------------
let lifetimeChart: Chart | null = null;
let performanceChart: Chart | null = null;

function destroyCharts(): void {
  lifetimeChart?.destroy();
  performanceChart?.destroy();
  lifetimeChart = performanceChart = null;
}

// ---------------------------------------------------------------------------
// Zod schema (mirrors Next.js FinDataSchema)
// ---------------------------------------------------------------------------
const FinDataSchema = z.object({
  electr_price:   z.coerce.number().gte(0, { message: 'Must be between 0 and 1000' }).lte(1000, { message: 'Must be between 0 and 1000' }),
  feed_in_tariff: z.coerce.number().gte(0, { message: 'Must be between 0 and 1000' }).lte(1000, { message: 'Must be between 0 and 1000' }),
  pv_price:       z.coerce.number().gte(0, { message: 'Must be between 0 and 10,000' }).lte(10000, { message: 'Must be between 0 and 10,000' }),
  battery_price:  z.coerce.number().gte(0, { message: 'Must be between 0 and 10,000' }).lte(10000, { message: 'Must be between 0 and 10,000' }),
  useful_life:    z.coerce.number().gte(0, { message: 'Must be between 0 and 50' }).lte(50, { message: 'Must be between 0 and 50' }),
  module_deg:     z.coerce.number().gt(0,  { message: 'Must be between 0 and 100 (exclusive)' }).lt(100, { message: 'Must be between 0 and 100 (exclusive)' }),
  inflation:      z.coerce.number().gte(0, { message: 'Must be between 0 and 100' }).lte(100, { message: 'Must be between 0 and 100' }),
  op_cost:        z.coerce.number().gte(0, { message: 'Must be between 0 and 100' }).lte(100, { message: 'Must be between 0 and 100' }),
  down_payment:   z.coerce.number().gte(0, { message: 'Must be between 0 and 100' }).lte(100, { message: 'Must be between 0 and 100' }),
  pay_off_rate:   z.coerce.number().gte(0, { message: 'Must be between 0 and 100' }).lte(100, { message: 'Must be between 0 and 100' }),
  interest_rate:  z.coerce.number().gte(0, { message: 'Must be between 0 and 100' }).lte(100, { message: 'Must be between 0 and 100' }),
});

// ---------------------------------------------------------------------------
// Default form values
// ---------------------------------------------------------------------------
const FIN_DEFAULTS: Omit<FinData, 'model_id'> = {
  electr_price: 45, feed_in_tariff: 8, pv_price: 1500, battery_price: 650,
  useful_life: 20, module_deg: 0.5, inflation: 3, op_cost: 1,
  down_payment: 25, pay_off_rate: 10, interest_rate: 5,
};

// ---------------------------------------------------------------------------
// Roof orientation mapping
// ---------------------------------------------------------------------------
const ORIENTATION_MAP: Record<number, string> = {
  0: 'South', 45: 'South-West', 90: 'West', 135: 'North-West', 180: 'North',
  [-45]: 'South-East', [-90]: 'East', [-135]: 'North-East',
};

function orientationName(deg: number): string {
  return ORIENTATION_MAP[deg] ?? 'Unknown Orientation';
}

// ---------------------------------------------------------------------------
// Chart colours
// ---------------------------------------------------------------------------
const COLORS = {
  darkGreen:  '#15803d',
  medGreen:   '#16a34a',
  lightGreen: '#4ade80',
  darkRed:    '#b91c1c',
  lightRed:   '#f87171',
  blue:       '#3b82f6',
  orange:     '#f97316',
  red:        '#ef4444',
};

// ---------------------------------------------------------------------------
// SVG icons
// ---------------------------------------------------------------------------
const icons = {
  bolt:    `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>`,
  sun:     `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg>`,
  battery: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4z"/></svg>`,
  clock:   `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/></svg>`,
  trend:   `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>`,
  wrench:  `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>`,
  dollar:  `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>`,
  mapPin:  `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>`,
  roofIncl:`<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>`,
  compass: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13l-2 6 6-2-4-4zm1 5.9c-.5 0-.9-.4-.9-.9s.4-.9.9-.9.9.4.9.9-.4.9-.9.9z"/></svg>`,
  play:    `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>`,
  eye:     `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>`,
};

// ---------------------------------------------------------------------------
// Field definitions (data-driven — used for form HTML and form population)
// ---------------------------------------------------------------------------
type FieldDef = {
  key: keyof Omit<FinData, 'model_id'>;
  label: string;
  unit: string;
  step: string;
  icon: string;
};

const FIELDS: FieldDef[] = [
  { key: 'electr_price',   label: 'Electricity price',  unit: 'ct/kWh', step: '0.1', icon: icons.bolt    },
  { key: 'feed_in_tariff', label: 'Feed-in tariff',     unit: 'ct/kWh', step: '0.1', icon: icons.sun     },
  { key: 'pv_price',       label: 'PV price',           unit: '€/kWp',  step: '1',   icon: icons.sun     },
  { key: 'battery_price',  label: 'Battery price',      unit: '€/kWh',  step: '1',   icon: icons.battery },
  { key: 'useful_life',    label: 'Useful life',         unit: 'years',  step: '1',   icon: icons.clock   },
  { key: 'module_deg',     label: 'Module degradation', unit: '%',      step: '0.1', icon: icons.trend   },
  { key: 'inflation',      label: 'Inflation',          unit: '%',      step: '0.1', icon: icons.trend   },
  { key: 'op_cost',        label: 'Operation cost',     unit: '%',      step: '0.1', icon: icons.wrench  },
  { key: 'down_payment',   label: 'Down payment',       unit: '%',      step: '0.1', icon: icons.dollar  },
  { key: 'pay_off_rate',   label: 'Pay off rate',       unit: '%',      step: '0.1', icon: icons.dollar  },
  { key: 'interest_rate',  label: 'Interest rate',      unit: '%',      step: '0.1', icon: icons.dollar  },
];

// ---------------------------------------------------------------------------
// Form error helpers (same conventions as models.ts)
// ---------------------------------------------------------------------------
function clearErrors(form: HTMLFormElement): void {
  form.querySelectorAll<HTMLSpanElement>('.form-error').forEach((el) => { el.textContent = ''; });
  form.querySelectorAll<HTMLElement>('.form-input').forEach((el) => el.classList.remove('error'));
}

function showFieldError(fieldName: string, message: string): void {
  const errEl = document.getElementById(`err-${fieldName}`);
  const inputEl = document.getElementById(`f-${fieldName}`);
  if (errEl) errEl.textContent = message;
  if (inputEl) inputEl.classList.add('error');
}

// ---------------------------------------------------------------------------
// Number formatting helpers
// ---------------------------------------------------------------------------
function fmtEuro(n: number): string {
  return `€ ${n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

function fmtOne(n: number): string {
  return n.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

// ---------------------------------------------------------------------------
// HTML builders
// ---------------------------------------------------------------------------

function pageShellHTML(): string {
  return `
    <div class="fin-page">
      <h1 class="page-heading">Finances</h1>
      <div class="sim-layout">
        <aside class="sim-sidebar" id="fin-sidebar">
          <p class="sidebar-loading">Loading…</p>
        </aside>
        <section class="sim-content" id="fin-content">
          <div class="card"><div class="centered-card-text">Loading…</div></div>
        </section>
      </div>
    </div>`;
}

function finFormFieldsHTML(values: Omit<FinData, 'model_id'>): string {
  return FIELDS.map((f) => `
    <div class="form-group">
      <label class="form-label" for="f-${f.key}">
        <span class="form-label-icon">${f.icon}</span>
        ${f.label} <span class="field-unit">(${f.unit})</span>
      </label>
      <input id="f-${f.key}" name="${f.key}" type="number" step="${f.step}"
             class="form-input" value="${values[f.key]}">
      <span class="form-error" id="err-${f.key}"></span>
    </div>`).join('');
}

function noSimWarningHTML(modelId: string): string {
  return `
    <div class="fin-warning">
      Please run a simulation before calculating finances.
      <a href="/workspace/simulations/${modelId}" data-link class="fin-warning-link">
        <strong>Run simulation →</strong>
      </a>
    </div>`;
}

function sidebarFormHTML(
  model: ModelData,
  values: Omit<FinData, 'model_id'>,
): string {
  const hasSim = !!model.sim_id;
  const mid = model.model_id!;

  const calculateBtn = hasSim
    ? `<button class="btn btn-blue" id="btn-calculate" type="button">
         ${icons.play} Calculate Finances
       </button>`
    : `${noSimWarningHTML(mid)}
       <button class="btn btn-blue" id="btn-calculate" type="button" disabled>
         ${icons.play} Calculate Finances
       </button>`;

  const viewSimBtn = hasSim
    ? `<button class="btn btn-green" data-action="view-sim" data-model-id="${mid}" type="button">
         ${icons.eye} View Simulation Results
       </button>`
    : '';

  return `
    <form id="fin-form" class="fin-form" novalidate>
      ${finFormFieldsHTML(values)}
      <div class="sidebar-actions">
        ${calculateBtn}
        ${viewSimBtn}
      </div>
    </form>`;
}

function sidebarHTML(
  models: ModelData[],
  selectedId: string | null,
  finDataList: FinData[],
): string {
  if (models.length === 0) {
    return `<p class="sidebar-empty">Please <a href="/workspace/models" data-link>create a model</a> first.</p>`;
  }

  const selectedModel = models.find((m) => m.model_id === selectedId) ?? models[0];
  const savedFinData = finDataList.find((f) => f.model_id === selectedModel.model_id);
  const formValues = savedFinData
    ? (({ model_id: _id, ...rest }) => rest)(savedFinData)
    : FIN_DEFAULTS;

  const options = models
    .map(
      (m) =>
        `<option value="${m.model_id}" ${m.model_id === selectedId ? 'selected' : ''}>${m.model_name}</option>`,
    )
    .join('');

  return `
    <select id="model-select" class="sidebar-select">${options}</select>
    ${sidebarFormHTML(selectedModel, formValues)}`;
}

function defaultContentHTML(): string {
  return `<div class="card"><div class="centered-card-text">Set up finances to view results</div></div>`;
}

function noSimContentHTML(modelId: string): string {
  return `
    <div class="card">
      <div class="card-header"><span class="card-title">Simulation Required</span></div>
      <div class="card-body">
        <p class="centered-card-text" style="margin-bottom:1.5rem;">
          This model has not been simulated yet.<br>
          Run a simulation first before calculating finances.
        </p>
        <div style="display:flex;justify-content:center;">
          <button class="btn btn-blue" data-action="run-sim" data-model-id="${modelId}" type="button">
            ${icons.play} Run Simulation
          </button>
        </div>
      </div>
    </div>`;
}

function noResultsCardHTML(): string {
  return `<div class="card"><div class="centered-card-text">No results found. Calculate finances to get results.</div></div>`;
}

function finResultsGridHTML(): string {
  return `
    <div class="fin-grid">
      <div class="fin-grid-top">
        <div class="card" id="card-model-summary"></div>
        <div class="card" id="card-kpis"></div>
        <div class="card" id="card-lifetime">
          <div class="card-header"><span class="card-title">Performance over Lifetime</span></div>
          <div class="card-body">
            <div class="chart-wrap chart-wrap--tall"><canvas id="canvas-lifetime"></canvas></div>
          </div>
        </div>
      </div>
      <div class="fin-grid-bottom">
        <div class="card">
          <div class="card-header"><span class="card-title">Financial Performance</span></div>
          <div class="card-body">
            <div class="chart-wrap chart-wrap--tall"><canvas id="canvas-performance"></canvas></div>
          </div>
        </div>
      </div>
    </div>`;
}

function modelSummaryHTML(model: ModelData): string {
  return `
    <div class="card-header"><span class="card-title">Model Summary</span></div>
    <div class="card-body">
      <div class="summary-grid">
        <div class="summary-row">${icons.mapPin}  <span class="summary-label">Location</span>    <span class="summary-value">${model.location}</span></div>
        <div class="summary-row">${icons.roofIncl}<span class="summary-label">Roof incl.</span>  <span class="summary-value">${model.roof_incl}°</span></div>
        <div class="summary-row">${icons.compass} <span class="summary-label">Orientation</span> <span class="summary-value">${orientationName(model.roof_azimuth)}</span></div>
        <div class="summary-row">${icons.bolt}    <span class="summary-label">Consumption</span> <span class="summary-value">${model.electr_cons} kWh</span></div>
        <div class="summary-row">${icons.sun}     <span class="summary-label">PV peak power</span><span class="summary-value">${model.peak_power} kWp</span></div>
        <div class="summary-row">${icons.battery} <span class="summary-label">Battery cap.</span><span class="summary-value">${model.battery_cap} kWh</span></div>
      </div>
    </div>`;
}

function kpiCardHTML(kpis: FinKPIs): string {
  const rows: [string, string, string][] = [
    [icons.dollar,  'Total investment', fmtEuro(kpis.investment.total)],
    [icons.trend,   'Cum. profit',      fmtEuro(kpis.cum_profit)],
    [icons.clock,   'Break-even',       `${fmtOne(kpis.break_even_year)} years`],
    [icons.dollar,  'Total loan',       fmtEuro(kpis.loan)],
    [icons.clock,   'Loan paid off',    `${fmtOne(kpis.loan_paid_off)} years`],
    [icons.bolt,    'LCOE',             `${fmtOne(kpis.lcoe)} ct/kWh`],
    [icons.trend,   'ROI',              `${fmtOne(kpis.solar_interest_rate)} %`],
  ];

  const rowsHTML = rows
    .map(
      ([icon, label, value]) => `
      <div class="kpi-row">
        <span class="kpi-label">${icon} ${label}</span>
        <span class="kpi-value">${value}</span>
      </div>`,
    )
    .join('');

  return `
    <div class="card-header"><span class="card-title">Key Performance Indicators</span></div>
    <div class="card-body">
      <div class="kpi-list">${rowsHTML}</div>
    </div>`;
}

// ---------------------------------------------------------------------------
// Chart renderers
// ---------------------------------------------------------------------------

function renderLifetimeChart(kpis: FinKPIs): void {
  const canvas = document.getElementById('canvas-lifetime') as HTMLCanvasElement | null;
  if (!canvas) return;

  lifetimeChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: ['Investment', 'Revenue'],
      datasets: [
        {
          label: 'PV cost',
          data: [kpis.investment.pv, 0],
          backgroundColor: COLORS.darkRed,
          stack: 'investment',
        },
        {
          label: 'Battery cost',
          data: [kpis.investment.battery, 0],
          backgroundColor: COLORS.lightRed,
          stack: 'investment',
        },
        {
          label: 'Cost savings',
          data: [0, kpis.cum_cost_savings],
          backgroundColor: COLORS.lightGreen,
          stack: 'revenue',
        },
        {
          label: 'Feed-in revenue',
          data: [0, kpis.cum_feed_in_revenue],
          backgroundColor: COLORS.medGreen,
          stack: 'revenue',
        },
        {
          label: 'Operation costs',
          data: [0, -kpis.cum_operation_costs],
          backgroundColor: COLORS.darkGreen,
          stack: 'revenue',
        },
      ],
    },
    options: {
      plugins: {
        legend: { display: true, position: 'bottom' },
      },
      scales: {
        x: { stacked: true },
        y: {
          stacked: true,
          ticks: { callback: (v) => `€ ${v}` },
        },
      },
    },
  });
}

function renderPerformanceChart(yearlyData: FinYearlyData[], investmentTotal: number): void {
  const canvas = document.getElementById('canvas-performance') as HTMLCanvasElement | null;
  if (!canvas) return;

  const labels = yearlyData.map((d) => String(d.year));

  performanceChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Cum. Profit',
          data: yearlyData.map((d) => d.cum_profit),
          borderColor: COLORS.darkGreen,
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
        },
        {
          label: 'Investment',
          data: yearlyData.map(() => -investmentTotal),
          borderColor: COLORS.red,
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [5, 5],
          pointRadius: 0,
          tension: 0,
        },
        {
          label: 'Cum. Cash Flow',
          data: yearlyData.map((d) => d.cum_cash_flow),
          borderColor: COLORS.blue,
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
        },
        {
          label: 'Loan',
          data: yearlyData.map((d) => d.loan),
          borderColor: COLORS.orange,
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
        },
      ],
    },
    options: {
      animation: false,
      plugins: {
        legend: { display: true, position: 'bottom' },
      },
      scales: {
        y: {
          ticks: { callback: (v) => `€ ${v}` },
        },
      },
    },
  });
}

// ---------------------------------------------------------------------------
// Finance results renderer
// ---------------------------------------------------------------------------
async function renderFinResults(
  modelId: string,
  models: ModelData[],
): Promise<void> {
  const contentEl = document.getElementById('fin-content');
  if (!contentEl) return;

  let finResults: FinResults | null = null;
  try {
    finResults = await fetchFinResults(modelId);
  } catch {
    contentEl.innerHTML = noResultsCardHTML();
    return;
  }

  if (!finResults) {
    contentEl.innerHTML = noResultsCardHTML();
    return;
  }

  const model = models.find((m) => m.model_id === modelId);
  if (!model) {
    contentEl.innerHTML = noResultsCardHTML();
    return;
  }

  // Inject grid scaffold
  contentEl.innerHTML = finResultsGridHTML();

  // Populate static cards
  const summaryEl = document.getElementById('card-model-summary');
  if (summaryEl) summaryEl.innerHTML = modelSummaryHTML(model);

  const kpiEl = document.getElementById('card-kpis');
  if (kpiEl) kpiEl.innerHTML = kpiCardHTML(finResults.fin_kpis);

  // Render charts
  renderLifetimeChart(finResults.fin_kpis);
  renderPerformanceChart(finResults.yearly_data, finResults.fin_kpis.investment.total);
}

// ---------------------------------------------------------------------------
// Sidebar renderer
// ---------------------------------------------------------------------------
function renderSidebar(
  models: ModelData[],
  selectedId: string | null,
  finDataList: FinData[],
): void {
  const sidebarEl = document.getElementById('fin-sidebar');
  if (!sidebarEl) return;
  sidebarEl.innerHTML = sidebarHTML(models, selectedId, finDataList);
}

// ---------------------------------------------------------------------------
// Form submission handler
// ---------------------------------------------------------------------------
async function handleCalculate(
  form: HTMLFormElement,
  model: ModelData,
): Promise<void> {
  clearErrors(form);

  const raw = Object.fromEntries(new FormData(form));
  const result = FinDataSchema.safeParse(raw);

  if (!result.success) {
    const errs = result.error.flatten().fieldErrors;
    for (const [field, msgs] of Object.entries(errs)) {
      if (msgs?.[0]) showFieldError(field, msgs[0]);
    }
    return;
  }

  const payload: FinData = { model_id: model.model_id!, ...result.data };

  showLoadingOverlay('Calculating your system\'s finances ...');
  try {
    await submitFinFormData(payload);
    hideLoadingOverlay();
    navigate(`/workspace/finances/${model.model_id}`);
  } catch {
    hideLoadingOverlay();
    showFieldError('electr_price', 'Submission failed. Please try again.');
  }
}

// ---------------------------------------------------------------------------
// Sidebar event listeners (event delegation)
// ---------------------------------------------------------------------------
function attachSidebarListeners(
  container: HTMLElement,
  models: ModelData[],
  finDataList: FinData[],
): void {
  const signal = listenerController!.signal;

  // Dropdown change → navigate to the selected model (always keep model_id in URL)
  container.addEventListener('change', (e) => {
    const sel = (e.target as HTMLElement).closest<HTMLSelectElement>('#model-select');
    if (!sel) return;
    navigate(`/workspace/finances/${sel.value}`);
  }, { signal });

  // Button clicks via data-action and #btn-calculate
  container.addEventListener('click', async (e) => {
    const target = e.target as HTMLElement;

    // Calculate button
    const calcBtn = target.closest<HTMLButtonElement>('#btn-calculate');
    if (calcBtn && !calcBtn.disabled) {
      const form = document.getElementById('fin-form') as HTMLFormElement | null;
      // Find the currently selected model
      const sel = document.getElementById('model-select') as HTMLSelectElement | null;
      const modelId = sel?.value ?? null;
      const model = models.find((m) => m.model_id === modelId);
      if (form && model) await handleCalculate(form, model);
      return;
    }

    // data-action buttons
    const btn = target.closest<HTMLButtonElement>('[data-action]');
    if (!btn) return;

    const action = btn.dataset.action!;
    const modelId = btn.dataset.modelId!;

    if (action === 'view-sim') {
      navigate(`/workspace/simulations/${modelId}`);
      return;
    }
  }, { signal });
}

// ---------------------------------------------------------------------------
// Page entry point
// ---------------------------------------------------------------------------
export async function render(
  container: HTMLElement,
  params?: Record<string, string>,
): Promise<void> {
  const modelId = params?.model_id ?? null;

  // Revoke previous render's listeners, issue a fresh controller
  listenerController?.abort();
  listenerController = new AbortController();

  // Destroy any live charts
  destroyCharts();

  // Inject shell immediately — no blank page during async fetch
  container.innerHTML = pageShellHTML();

  // Parallel fetch: models + fin form data
  let models: ModelData[] = [];
  let finDataList: FinData[] = [];
  try {
    [models, finDataList] = await Promise.all([fetchModels(), fetchFinFormData()]);
  } catch {
    const sidebarEl = document.getElementById('fin-sidebar');
    if (sidebarEl) {
      sidebarEl.innerHTML = `<p class="sidebar-error">Failed to load data.</p>`;
    }
    return;
  }

  // Render sidebar
  renderSidebar(models, modelId, finDataList);

  // Attach listeners
  attachSidebarListeners(container, models, finDataList);

  // Content area
  const contentEl = document.getElementById('fin-content');
  if (!contentEl) return;

  if (!modelId) {
    contentEl.innerHTML = defaultContentHTML();
    return;
  }

  // Find the selected model
  const selectedModel = models.find((m) => m.model_id === modelId);

  // If the model has never been simulated, prompt the user to run a simulation
  if (!selectedModel?.sim_id) {
    contentEl.innerHTML = noSimContentHTML(modelId);
    // Wire the "Run Simulation" button in the content area
    const signal = listenerController!.signal;
    contentEl.addEventListener('click', (e) => {
      const btn = (e.target as HTMLElement).closest<HTMLButtonElement>('[data-action="run-sim"]');
      if (!btn) return;
      navigate(`/workspace/simulations/${btn.dataset.modelId}`);
    }, { signal });
    return;
  }

  // Only show results if a calculation has previously been run for this model
  const hasFin = finDataList.some((f) => f.model_id === modelId);
  if (!hasFin) {
    contentEl.innerHTML = defaultContentHTML();
    return;
  }

  await renderFinResults(modelId, models);
}
