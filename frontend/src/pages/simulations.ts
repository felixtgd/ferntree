// Simulations page — handles both /workspace/simulations and
// /workspace/simulations/:model_id

import {
  Chart,
  ArcElement,
  DoughnutController,
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
import type { Plugin } from 'chart.js';
import { fetchModels, fetchSimResults, fetchSimTimeseries, runSimulation } from '../api';
import { navigate } from '../router';
import { showLoadingOverlay, hideLoadingOverlay } from '../overlay';
import type { ModelData, SimResultsEval, SimTimestep } from '../types';

Chart.register(
  ArcElement,
  DoughnutController,
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
// Listener lifecycle — abort controller revokes all container event listeners
// registered by the previous render before a new one starts.
// ---------------------------------------------------------------------------
let listenerController: AbortController | null = null;

// ---------------------------------------------------------------------------
// Chart instance holders — destroyed before every re-render to avoid
// "Canvas already in use" errors.
// ---------------------------------------------------------------------------
let consumptionChart: Chart | null = null;
let pvGenChart: Chart | null = null;
let monthlyChart: Chart | null = null;
let powerChart: Chart | null = null;
let socChart: Chart | null = null;

function destroyCharts(): void {
  [consumptionChart, pvGenChart, monthlyChart, powerChart, socChart].forEach(
    (c) => c?.destroy(),
  );
  consumptionChart = pvGenChart = monthlyChart = powerChart = socChart = null;
}

// ---------------------------------------------------------------------------
// Theme token helpers
// ---------------------------------------------------------------------------
function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// ---------------------------------------------------------------------------
// SVG icons (inline, 18×18)
// ---------------------------------------------------------------------------
const icons = {
  mapPin: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>`,
  roofIncl: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>`,
  compass: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13l-2 6 6-2-4-4zm1 5.9c-.5 0-.9-.4-.9-.9s.4-.9.9-.9.9.4.9.9-.4.9-.9.9z"/></svg>`,
  bolt: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>`,
  sun: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg>`,
  battery: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4z"/></svg>`,
  play: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>`,
  eye: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>`,
  dollar: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>`,
  info: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>`,
};

// ---------------------------------------------------------------------------
// HTML builders
// ---------------------------------------------------------------------------

function pageShellHTML(): string {
  return `
    <div class="sim-page">
      <h1 class="page-heading">Simulations</h1>
      <div class="sim-layout">
        <aside class="sim-sidebar" id="sim-sidebar">
          <p class="sidebar-loading">Loading models…</p>
        </aside>
        <section class="sim-content" id="sim-content">
          <div class="card"><div class="centered-card-text">Loading…</div></div>
        </section>
      </div>
    </div>`;
}

function sidebarParamsHTML(model: ModelData): string {
  return `
    <div class="sidebar-params">
      <div class="sidebar-param-row">
        <span class="sidebar-param-icon">${icons.mapPin}</span>
        <span class="sidebar-param-label" title="${model.coordinates?.display_name ?? model.location}">${model.location}</span>
      </div>
      <div class="sidebar-param-row">
        <span class="sidebar-param-icon">${icons.roofIncl}</span>
        <span class="sidebar-param-label">${model.roof_incl}°</span>
      </div>
      <div class="sidebar-param-row">
        <span class="sidebar-param-icon">${icons.compass}</span>
        <span class="sidebar-param-label">${model.roof_azimuth}°</span>
      </div>
      <div class="sidebar-param-row">
        <span class="sidebar-param-icon">${icons.bolt}</span>
        <span class="sidebar-param-label">${model.electr_cons} kWh</span>
      </div>
      <div class="sidebar-param-row">
        <span class="sidebar-param-icon">${icons.sun}</span>
        <span class="sidebar-param-label">${model.peak_power} kWp</span>
      </div>
      <div class="sidebar-param-row">
        <span class="sidebar-param-icon">${icons.battery}</span>
        <span class="sidebar-param-label">${model.battery_cap} kWh</span>
      </div>
    </div>`;
}

function sidebarActionsHTML(model: ModelData): string {
  const mid = model.model_id!;
  if (model.sim_id) {
    return `
      <div class="sidebar-actions">
        <button class="btn btn-green" data-action="view-sim" data-model-id="${mid}">
          ${icons.eye} View Simulation Results
        </button>
        <button class="btn btn-orange" data-action="go-fin" data-model-id="${mid}">
          ${icons.dollar} Go to Finances
        </button>
      </div>`;
  }
  return `
    <div class="sidebar-actions">
      <button class="btn btn-blue" data-action="run-sim" data-model-id="${mid}">
        ${icons.play} Run Simulation
      </button>
    </div>`;
}

function sidebarHTML(models: ModelData[], selectedId: string | null): string {
  if (models.length === 0) {
    return `<p class="sidebar-empty">Please <a href="/workspace/models" data-link>create a model</a> first.</p>`;
  }

  const selectedModel = models.find((m) => m.model_id === selectedId) ?? models[0];

  const options = models
    .map(
      (m) =>
        `<option value="${m.model_id}" ${m.model_id === selectedId ? 'selected' : ''}>${m.model_name}</option>`,
    )
    .join('');

  return `
    <select id="model-select" class="sidebar-select">${options}</select>
    ${sidebarParamsHTML(selectedModel)}
    ${sidebarActionsHTML(selectedModel)}`;
}

function defaultContentHTML(): string {
  return `<div class="card"><div class="centered-card-text">Run a simulation to view results</div></div>`;
}

function noResultsCardHTML(): string {
  return `<div class="card"><div class="centered-card-text">No results found. Run a simulation to get results.</div></div>`;
}

function resultsGridHTML(): string {
  return `
    <div class="sim-grid">
      <div class="sim-grid-top">
        <div class="card" id="card-consumption">
          <div class="card-header"><span class="card-title" id="title-consumption">Consumption</span></div>
          <div class="card-body">
            <div class="chart-wrap"><canvas id="canvas-consumption"></canvas></div>
            <div id="legend-consumption" class="donut-legend"></div>
          </div>
        </div>
        <div class="card" id="card-pvgen">
          <div class="card-header"><span class="card-title" id="title-pvgen">PV Generation</span></div>
          <div class="card-body">
            <div class="chart-wrap"><canvas id="canvas-pvgen"></canvas></div>
            <div id="legend-pvgen" class="donut-legend"></div>
          </div>
        </div>
        <div class="card" id="card-monthly">
          <div class="card-header"><span class="card-title">Monthly PV Generation</span></div>
          <div class="card-body">
            <div class="chart-wrap"><canvas id="canvas-monthly"></canvas></div>
          </div>
        </div>
      </div>
      <div class="sim-grid-bottom">
        <div class="date-range-row">
          <label class="date-label">From <input type="date" id="date-from" value="2023-06-19"></label>
          <label class="date-label">To <input type="date" id="date-to" value="2023-06-24"></label>
        </div>
        <div class="card">
          <div class="card-header"><span class="card-title">Power Profiles</span></div>
          <div class="card-body">
            <div class="chart-wrap chart-wrap--tall"><canvas id="canvas-power"></canvas></div>
          </div>
        </div>
        <div class="card card--mt">
          <div class="card-header"><span class="card-title">Battery State of Charge</span></div>
          <div class="card-body">
            <div class="chart-wrap chart-wrap--tall"><canvas id="canvas-soc"></canvas></div>
          </div>
        </div>
      </div>
    </div>`;
}

// ---------------------------------------------------------------------------
// Donut centre-label plugin factory (one per chart to avoid cross-canvas bleed)
// ---------------------------------------------------------------------------
function makeCentrePlugin(text: string): Plugin<'doughnut'> {
  return {
    id: 'centreLabel',
    afterDraw(chart) {
      const {
        ctx,
        chartArea: { top, right, bottom, left },
      } = chart;
      ctx.save();
      ctx.font = 'bold 20px sans-serif';
      ctx.fillStyle = cssVar('--text-primary');
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, (left + right) / 2, (top + bottom) / 2);
      ctx.restore();
    },
  };
}

// ---------------------------------------------------------------------------
// Legend HTML builder for donut charts
// ---------------------------------------------------------------------------
function donutLegendHTML(
  segments: { name: string; value: number; share: number; tooltip: string; swatchClass: string }[],
): string {
  return segments
    .map(
      (s) => `
      <div class="donut-legend-row">
        <span class="legend-swatch ${s.swatchClass}"></span>
        <span class="legend-name">${s.name}</span>
        <span class="legend-value">${s.value.toLocaleString('en-US', { maximumFractionDigits: 0 })} kWh</span>
        <span class="legend-share">${(s.share * 100).toFixed(1)}%</span>
        <span class="legend-info" title="${s.tooltip}">${icons.info}</span>
      </div>`,
    )
    .join('');
}

// ---------------------------------------------------------------------------
// Chart renderers
// ---------------------------------------------------------------------------

function renderConsumptionDonut(simResults: SimResultsEval): void {
  const kpis = simResults.energy_kpis;
  const centreText = `${(kpis.self_sufficiency * 100).toFixed(0)}%`;

  const titleEl = document.getElementById('title-consumption');
  if (titleEl) {
    titleEl.textContent = `Consumption: ${kpis.annual_consumption.toLocaleString('en-US', { maximumFractionDigits: 0 })} kWh`;
  }

  const canvas = document.getElementById('canvas-consumption') as HTMLCanvasElement | null;
  if (!canvas) return;

  consumptionChart = new Chart<'doughnut'>(canvas, {
    type: 'doughnut',
    data: {
      labels: ['PV', 'Grid'],
      datasets: [
        {
          data: [kpis.self_consumption, kpis.grid_consumption],
          backgroundColor: [cssVar('--copper-raw'), cssVar('--border-metal')],
          borderWidth: 1,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          backgroundColor: cssVar('--bg-surface'),
          titleColor: cssVar('--text-primary'),
          bodyColor: cssVar('--text-secondary'),
          borderColor: cssVar('--border-metal'),
          borderWidth: 1,
        },
      },
    },
    plugins: [makeCentrePlugin(centreText)],
  });

  const legendEl = document.getElementById('legend-consumption');
  if (legendEl) {
    const total = kpis.self_consumption + kpis.grid_consumption;
    legendEl.innerHTML = donutLegendHTML([
      {
        name: 'PV',
        value: kpis.self_consumption,
        share: total > 0 ? kpis.self_consumption / total : 0,
        tooltip: 'Energy drawn directly from your PV system',
        swatchClass: 'legend-swatch--copper',
      },
      {
        name: 'Grid',
        value: kpis.grid_consumption,
        share: total > 0 ? kpis.grid_consumption / total : 0,
        tooltip: 'Energy drawn from the electricity grid',
        swatchClass: 'legend-swatch--border',
      },
    ]);
  }
}

function renderPVGenDonut(simResults: SimResultsEval): void {
  const kpis = simResults.energy_kpis;
  const centreText = `${(kpis.self_consumption_rate * 100).toFixed(0)}%`;

  const titleEl = document.getElementById('title-pvgen');
  if (titleEl) {
    titleEl.textContent = `PV Generation: ${kpis.pv_generation.toLocaleString('en-US', { maximumFractionDigits: 0 })} kWh`;
  }

  const canvas = document.getElementById('canvas-pvgen') as HTMLCanvasElement | null;
  if (!canvas) return;

  pvGenChart = new Chart<'doughnut'>(canvas, {
    type: 'doughnut',
    data: {
      labels: ['Self-cons.', 'Grid feed-in'],
      datasets: [
        {
          data: [kpis.self_consumption, kpis.grid_feed_in],
          backgroundColor: [cssVar('--copper-raw'), cssVar('--border-metal')],
          borderWidth: 1,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          backgroundColor: cssVar('--bg-surface'),
          titleColor: cssVar('--text-primary'),
          bodyColor: cssVar('--text-secondary'),
          borderColor: cssVar('--border-metal'),
          borderWidth: 1,
        },
      },
    },
    plugins: [makeCentrePlugin(centreText)],
  });

  const legendEl = document.getElementById('legend-pvgen');
  if (legendEl) {
    const total = kpis.self_consumption + kpis.grid_feed_in;
    legendEl.innerHTML = donutLegendHTML([
      {
        name: 'Self-cons.',
        value: kpis.self_consumption,
        share: total > 0 ? kpis.self_consumption / total : 0,
        tooltip: 'PV energy consumed directly on-site',
        swatchClass: 'legend-swatch--copper',
      },
      {
        name: 'Grid feed-in',
        value: kpis.grid_feed_in,
        share: total > 0 ? kpis.grid_feed_in / total : 0,
        tooltip: 'Surplus PV energy exported to the grid',
        swatchClass: 'legend-swatch--border',
      },
    ]);
  }
}

function renderMonthlyBar(simResults: SimResultsEval): void {
  const canvas = document.getElementById('canvas-monthly') as HTMLCanvasElement | null;
  if (!canvas) return;

  const labels = simResults.pv_monthly_gen.map((m) => m.month);
  const data = simResults.pv_monthly_gen.map((m) => m.pv_generation);

  monthlyChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'PV Generation',
          data,
          backgroundColor: cssVar('--copper-raw'),
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          ticks: { color: cssVar('--text-secondary') },
          grid: { color: cssVar('--border-metal') },
        },
        y: {
          ticks: {
            color: cssVar('--text-secondary'),
            callback: (v) => `${v} kWh`,
          },
          grid: { color: cssVar('--border-metal') },
        },
      },
    },
  });
}

function renderTimeseriesCharts(timeseries: SimTimestep[]): void {
  const labels = timeseries.map((t) => t.time);

  // Power Profiles chart
  const powerCanvas = document.getElementById('canvas-power') as HTMLCanvasElement | null;
  if (powerCanvas) {
    powerChart = new Chart(powerCanvas, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Load',
            data: timeseries.map((t) => t.Load),
            borderColor: cssVar('--danger-red'),
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.3,
          },
          {
            label: 'PV',
            data: timeseries.map((t) => t.PV),
            borderColor: cssVar('--copper-raw'),
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.3,
          },
          {
            label: 'Battery',
            data: timeseries.map((t) => t.Battery),
            borderColor: cssVar('--copper-oxidized'),
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.3,
          },
          {
            label: 'Total',
            data: timeseries.map((t) => t.Total),
            borderColor: cssVar('--text-secondary'),
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.3,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        animation: false,
        plugins: {
          legend: {
            display: true,
            position: 'bottom',
            labels: { color: cssVar('--text-primary') },
          },
          tooltip: {
            backgroundColor: cssVar('--bg-surface'),
            titleColor: cssVar('--text-primary'),
            bodyColor: cssVar('--text-secondary'),
            borderColor: cssVar('--border-metal'),
            borderWidth: 1,
          },
        },
        scales: {
          x: {
            ticks: { maxTicksLimit: 2, color: cssVar('--text-secondary') },
            grid: { color: cssVar('--border-metal') },
          },
          y: {
            ticks: {
              color: cssVar('--text-secondary'),
              callback: (v) => `${v} kW`,
            },
            grid: { color: cssVar('--border-metal') },
          },
        },
      },
    });
  }

  // Battery State of Charge chart
  const socCanvas = document.getElementById('canvas-soc') as HTMLCanvasElement | null;
  if (socCanvas) {
    socChart = new Chart(socCanvas, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'State of Charge',
            data: timeseries.map((t) => t.StateOfCharge),
            borderColor: cssVar('--copper-oxidized'),
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.3,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        animation: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: cssVar('--bg-surface'),
            titleColor: cssVar('--text-primary'),
            bodyColor: cssVar('--text-secondary'),
            borderColor: cssVar('--border-metal'),
            borderWidth: 1,
          },
        },
        scales: {
          x: {
            ticks: { maxTicksLimit: 2, color: cssVar('--text-secondary') },
            grid: { color: cssVar('--border-metal') },
          },
          y: {
            min: 0,
            max: 100,
            ticks: {
              color: cssVar('--text-secondary'),
              callback: (v) => `${v}%`,
            },
            grid: { color: cssVar('--border-metal') },
          },
        },
      },
    });
  }
}

// ---------------------------------------------------------------------------
// Timeseries update (called on date-input change)
// ---------------------------------------------------------------------------
async function updateTimeseries(modelId: string): Promise<void> {
  const dateFrom =
    (document.getElementById('date-from') as HTMLInputElement | null)?.value ?? '2023-06-19';
  const dateTo =
    (document.getElementById('date-to') as HTMLInputElement | null)?.value ?? '2023-06-24';

  // Destroy existing timeseries charts and re-create with new data
  powerChart?.destroy();
  powerChart = null;
  socChart?.destroy();
  socChart = null;

  let timeseries: SimTimestep[] = [];
  try {
    timeseries = await fetchSimTimeseries(modelId, dateFrom, dateTo);
  } catch {
    // leave timeseries empty; no-results guard below will handle it
  }

  if (timeseries.length === 0) {
    const powerCanvas = document.getElementById('canvas-power') as HTMLCanvasElement | null;
    const socCanvas = document.getElementById('canvas-soc') as HTMLCanvasElement | null;
    if (powerCanvas) powerCanvas.closest('.card-body')!.innerHTML = `<div class="centered-card-text">No data for selected date range.</div>`;
    if (socCanvas) socCanvas.closest('.card-body')!.innerHTML = `<div class="centered-card-text">No data for selected date range.</div>`;
    return;
  }

  renderTimeseriesCharts(timeseries);
}

// ---------------------------------------------------------------------------
// Full results renderer
// ---------------------------------------------------------------------------
async function renderSimResults(container: HTMLElement, modelId: string): Promise<void> {
  const contentEl = container.querySelector<HTMLElement>('#sim-content');
  if (!contentEl) return;

  let simResults: SimResultsEval | null = null;
  try {
    simResults = await fetchSimResults(modelId);
  } catch {
    contentEl.innerHTML = noResultsCardHTML();
    return;
  }

  if (!simResults) {
    contentEl.innerHTML = noResultsCardHTML();
    return;
  }

  // Inject the full results grid
  contentEl.innerHTML = resultsGridHTML();

  // Render static charts
  renderConsumptionDonut(simResults);
  renderPVGenDonut(simResults);
  renderMonthlyBar(simResults);

  // Fetch and render timeseries with defaults
  let timeseries: SimTimestep[] = [];
  try {
    timeseries = await fetchSimTimeseries(modelId, '2023-06-19', '2023-06-24');
  } catch {
    // empty array — guard below handles it
  }

  if (timeseries.length > 0) {
    renderTimeseriesCharts(timeseries);
  }

  // Attach date-change listeners
  const dateFrom = document.getElementById('date-from') as HTMLInputElement | null;
  const dateTo = document.getElementById('date-to') as HTMLInputElement | null;
  dateFrom?.addEventListener('change', () => updateTimeseries(modelId));
  dateTo?.addEventListener('change', () => updateTimeseries(modelId));
}

// ---------------------------------------------------------------------------
// Sidebar renderer
// ---------------------------------------------------------------------------
function renderSidebar(models: ModelData[], selectedId: string | null): void {
  const sidebarEl = document.getElementById('sim-sidebar');
  if (!sidebarEl) return;
  sidebarEl.innerHTML = sidebarHTML(models, selectedId);
}

// ---------------------------------------------------------------------------
// Sidebar event listeners (event delegation)
// ---------------------------------------------------------------------------
function attachSidebarListeners(
  container: HTMLElement,
  models: ModelData[],
): void {
  const signal = listenerController!.signal;

  // Dropdown change → navigate to that model's results
  container.addEventListener('change', (e) => {
    const sel = (e.target as HTMLElement).closest<HTMLSelectElement>('#model-select');
    if (!sel) return;
    navigate(`/workspace/simulations/${sel.value}`);
  }, { signal });

  // Button clicks via data-action
  container.addEventListener('click', async (e) => {
    const btn = (e.target as HTMLElement).closest<HTMLButtonElement>('[data-action]');
    if (!btn) return;

    const action = btn.dataset.action!;
    const modelId = btn.dataset.modelId!;

    if (action === 'view-sim') {
      navigate(`/workspace/simulations/${modelId}`);
      return;
    }

    if (action === 'go-fin') {
      navigate(`/workspace/finances/${modelId}`);
      return;
    }

    if (action === 'run-sim') {
      showLoadingOverlay('Simulating your energy system ...');
      try {
        const result = await runSimulation(modelId);
        if (result.run_successful) {
          hideLoadingOverlay();
          navigate(`/workspace/simulations/${modelId}`);
        } else {
          hideLoadingOverlay();
          // Re-fetch models and refresh sidebar to reflect any state change
          const refreshed = await fetchModels().catch(() => models);
          renderSidebar(refreshed, modelId);
        }
      } catch {
        hideLoadingOverlay();
        const refreshed = await fetchModels().catch(() => models);
        renderSidebar(refreshed, modelId);
      }
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

  // Revoke all event listeners registered by the previous render, then issue
  // a fresh controller for this render's listeners.
  listenerController?.abort();
  listenerController = new AbortController();

  // Destroy any charts from a previous render before touching the DOM
  destroyCharts();

  // Inject the shell immediately (no blank page during async fetch)
  container.innerHTML = pageShellHTML();

  // Fetch models
  let models: ModelData[] = [];
  try {
    models = await fetchModels();
  } catch {
    const sidebarEl = document.getElementById('sim-sidebar');
    if (sidebarEl) {
      sidebarEl.innerHTML = `<p class="sidebar-error">Failed to load models.</p>`;
    }
    return;
  }

  // Render sidebar
  renderSidebar(models, modelId);

  // Attach sidebar event listeners
  attachSidebarListeners(container, models);

  // Render the content area
  const contentEl = document.getElementById('sim-content');
  if (!contentEl) return;

  if (!modelId) {
    contentEl.innerHTML = defaultContentHTML();
    return;
  }

  // Only fetch results if the model has actually been simulated.
  const selectedModel = models.find((m) => m.model_id === modelId);
  if (!selectedModel?.sim_id) {
    contentEl.innerHTML = defaultContentHTML();
    return;
  }

  await renderSimResults(container, modelId);
}
