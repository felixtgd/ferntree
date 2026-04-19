# Vanilla TypeScript Migration Plan

This document is a step-by-step guide for replacing the Next.js MVP frontend with a vanilla TypeScript application. It is intended to be precise enough for a new agent starting from a fresh session to follow without needing to read the full codebase first.

Read `nextjs_architecture.md` for a comprehensive reference of the current frontend. Read `nextjs_mvp.md` for the list of simplification changes already applied. Use `nextjs_checklist.md` as the acceptance test suite.

---

## Target Stack

| Concern | Technology |
|---|---|
| Language | TypeScript (compiled to ES modules) |
| Bundler | Vite |
| Styling | Plain CSS with CSS custom properties (no framework) |
| Charts | Chart.js |
| Routing | Client-side History API router (hand-rolled or `navigo`) |
| HTTP | `fetch` API called directly from the browser |
| Forms + validation | Native HTML forms; Zod for schema validation (client-side) |
| Icons | SVG inline or a CDN icon font (e.g. Remix Icon CSS) |
| No server runtime | Purely static HTML/CSS/JS — served from any static host |

---

## Key Architecture Changes

### 1. All API calls move to the browser

In Next.js, every backend call was made server-side (Server Components or Server Actions). The browser never contacted FastAPI directly.

In the vanilla app, the browser calls FastAPI directly over HTTP. This requires CORS to be configured on the backend.

**FastAPI CORS is already configured** (`backend/src/main.py` lines 50–59). The `allow_origins` list is populated from the `FRONTEND_BASE_URI` environment variable plus a wildcard. For local development add the vanilla app's origin (e.g. `http://localhost:5173`) to `FRONTEND_BASE_URI` in `backend/.env`. In production, set `FRONTEND_BASE_URI` to the deployed static host URL; remove the `"*"` wildcard for security.

### 2. No server secrets in the frontend

The only runtime configuration the vanilla frontend needs is the backend base URL. This can be:
- A hardcoded constant in a `config.ts` file for local development.
- A build-time environment variable injected by Vite (`import.meta.env.VITE_BACKEND_BASE_URI`).

Do not ship any secrets in the frontend bundle.

### 3. No `cache()`, no `revalidatePath()`

These are Next.js/React server-only concepts. In the vanilla app:
- Fetch data with a plain `fetch()` call each time a page loads.
- After a mutation (create model, run simulation, submit finances), re-fetch the affected data and re-render the relevant section.
- No framework-level cache invalidation is needed.

### 4. No Server Actions — replace with direct fetch calls

Every Server Action becomes a `fetch()` call in the browser. Validation moves to client-side Zod. The response handling (errors shown inline, redirect on success) is implemented in plain TypeScript.

### 5. Fixed user ID

All backend endpoints accept `user_id` as a query parameter. Use the fixed value `'mvp-user'` everywhere — no authentication infrastructure is needed.

### 6. Nominatim geocoding from the browser

In Next.js, Nominatim was called server-side in `models/actions.ts`. In the vanilla app, call it directly from the browser. Nominatim supports browser CORS requests natively — no proxy is needed. Include the `User-Agent` header (or `Referer` for browsers) to comply with OSM usage policy.

### 7. Routing

Use the History API (`history.pushState` / `history.replaceState`) with a simple client-side router. The router intercepts link clicks and renders the matching page component without a full page reload. The `popstate` event handles the browser back/forward buttons.

Recommended lightweight option: `navigo` (npm package). Alternative: hand-roll a ~50-line router using a route table and `window.location.pathname`.

### 8. Tremor → Chart.js + plain HTML

Tremor provides Cards, Dialogs, Inputs, Dropdowns, and Charts. All of these are replaced with:
- **Cards / layout**: plain `<div>` with CSS.
- **Dialogs**: native `<dialog>` element or a hand-rolled modal.
- **Inputs / selects**: native HTML form elements styled with CSS.
- **Charts**: Chart.js (`DonutChart` → `doughnut`, `BarChart` → `bar`, `LineChart` → `line`).
- **Tooltips**: native `title` attribute or a small CSS tooltip.

---

## Project Setup

### Directory structure

Create the vanilla app as a sibling to `frontend/`:

```
ferntree/
├── frontend/          # existing Next.js app (reference)
├── vanilla/           # new vanilla TS app
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── src/
│       ├── main.ts        # entry point — bootstraps router
│       ├── config.ts      # BACKEND_BASE_URI constant
│       ├── router.ts      # client-side router
│       ├── types.ts       # TypeScript types (ported from definitions.ts)
│       ├── api.ts         # all fetch wrappers
│       ├── styles/
│       │   └── global.css
│       └── pages/
│           ├── workspace.ts
│           ├── models.ts
│           ├── simulations.ts
│           ├── sim-results.ts
│           ├── finances.ts
│           └── fin-results.ts
```

### `package.json` dependencies

```json
{
  "dependencies": {
    "chart.js": "^4",
    "zod": "^3"
  },
  "devDependencies": {
    "vite": "^5",
    "typescript": "^5"
  }
}
```

Optional router: `"navigo": "^8"`.

### `vite.config.ts`

```typescript
import { defineConfig } from 'vite';

export default defineConfig({
  // Vite serves index.html from the project root by default.
  // For SPA routing, redirect all 404s back to index.html:
  server: {
    port: 5173,
  },
});
```

Add `"singleFile": true` or configure the preview server to serve `index.html` for all routes.

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true
  }
}
```

---

## TypeScript Types

Port all types from `frontend/app/utils/definitions.ts` verbatim to `vanilla/src/types.ts`. Remove `FormState` (Next.js Server Action envelope — not needed) and `EmailFormData` (contact form — not needed). All other types map 1:1 to the backend API shapes.

The types you need:

```
CoordinateData, ModelData, EnergyKPIs, PVMonthlyGen,
SimResultsEval, DonutChartData, SimTimestep,
FinData, FinInvestment, FinKPIs, FinYearlyData,
FinResults, FinChartData, FinBarChartItem
```

---

## API Layer (`api.ts`)

Implement one function per backend endpoint. All functions are `async` and return typed data or throw on error.

```typescript
const BASE = import.meta.env.VITE_BACKEND_BASE_URI ?? 'http://localhost:8000';
const USER_ID = 'mvp-user';

// 1. GET /workspace/models/fetch-models
export async function fetchModels(): Promise<ModelData[]>

// 2. POST /workspace/models/submit-model
export async function submitModel(payload: Omit<ModelData, 'model_id' | 'sim_id'>): Promise<string>

// 3. DELETE /workspace/models/delete-model
export async function deleteModel(model_id: string): Promise<boolean>

// 4. GET /workspace/simulations/run-sim
export async function runSimulation(model_id: string): Promise<{ run_successful: boolean }>

// 5. GET /workspace/simulations/fetch-sim-results
export async function fetchSimResults(model_id: string): Promise<SimResultsEval>

// 6. POST /workspace/simulations/fetch-sim-timeseries
export async function fetchSimTimeseries(model_id: string, date_from: string, date_to: string): Promise<SimTimestep[]>

// 7. GET /workspace/finances/fetch-fin-form-data
export async function fetchFinFormData(): Promise<FinData[]>

// 8. POST /workspace/finances/submit-fin-form-data
export async function submitFinFormData(payload: FinData): Promise<string>

// 9. GET /workspace/finances/fetch-fin-results
export async function fetchFinResults(model_id: string): Promise<FinResults>

// 10. Nominatim geocoding
export async function geocodeLocation(location: string): Promise<CoordinateData | null>
```

For the Nominatim call, set a `User-Agent` header:
```typescript
headers: { 'User-Agent': 'ferntree-app/1.0' }
```

For POST/DELETE requests include `?user_id=mvp-user` as a query parameter (same as the Next.js server actions). Do not include `user_id` in the POST body — the backend reads it from the query string only.

---

## Routing

### Routes table

| URL pattern | Page module | Notes |
|---|---|---|
| `/` | → redirect to `/workspace` | |
| `/workspace` | `workspace.ts` | Three workflow step cards |
| `/workspace/models` | `models.ts` | Model list, create form |
| `/workspace/simulations` | `simulations.ts` | Sidebar + default "run a simulation" prompt |
| `/workspace/simulations/:model_id` | `sim-results.ts` | Donut charts, bar chart, power line charts |
| `/workspace/finances` | `finances.ts` | Sidebar form + default prompt |
| `/workspace/finances/:model_id` | `fin-results.ts` | KPI card, bar chart, line chart |

### SPA setup

In `index.html`, include a single `<div id="app">` and load `main.ts`. The router renders each page by replacing `app.innerHTML` with the page's HTML string, then attaches event listeners.

Configure the Vite dev server (and production server) to serve `index.html` for all paths (`try_files $uri /index.html` in nginx).

### Active nav highlighting

The sidenav is rendered once and re-used across navigations. After each navigation, update active link highlighting by comparing `window.location.pathname` with `link.href` using `startsWith`:
```typescript
link.classList.toggle('active', window.location.pathname.startsWith(link.dataset.href!));
```

---

## Page Implementations

Each page module exports a `render(container: HTMLElement, params?: Record<string, string>): Promise<void>` function. The router calls `render` on every navigation.

### Layout

The persistent shell (sidenav + content area) is rendered once in `main.ts`. Individual page modules render only the right-hand content area.

Sidenav HTML structure:
```html
<nav id="sidenav">
  <a href="/workspace" data-link>Ferntree</a>
  <a href="/workspace/models" data-link data-href="/workspace/models">Models</a>
  <a href="/workspace/simulations" data-link data-href="/workspace/simulations">Simulations</a>
  <a href="/workspace/finances" data-link data-href="/workspace/finances">Finances</a>
</nav>
<main id="content"></main>
```

Intercept all clicks on `[data-link]` anchors and route via `history.pushState`.

### Workspace Home (`/workspace`)

Static HTML — three cards linking to Models, Simulations, Finances. No data fetch.

### Models (`/workspace/models`)

1. Fetch `fetchModels()` on page load.
2. Render a card per model with parameters and conditional action buttons (same logic as `nextjs_checklist.md` section 3).
3. **Create Model button**: disabled when `models.length >= 5` with tooltip text.
4. **Create Model dialog**: use `<dialog>` element. Open with `dialog.showModal()`. Submit the form: geocode the location first, then call `submitModel()`. Show Zod validation errors inline below each field.
5. **Run Simulation button**: show loading overlay → call `runSimulation()` → on success navigate to `/workspace/simulations/{model_id}`.
6. **Delete button**: call `deleteModel()` → re-render model list.

#### Form validation (client-side Zod, replaces server-side Zod)

Port `ModelDataSchema` from the Next.js server action to client-side validation using the same rules:
- `model_name`: 1–100 chars
- `location`: 1–100 chars (additionally: error if Nominatim returns no result)
- `roof_incl`: number 0–90
- `roof_azimuth`: number –180–180
- `electr_cons`, `peak_power`, `battery_cap`: number 0–100,000

### Simulations (`/workspace/simulations`)

The route `/workspace/simulations` and `/workspace/simulations/:model_id` share the same page module. Pass the `model_id` route param to the render function.

1. Fetch `fetchModels()` on load.
2. Render sidebar: model dropdown, selected model's parameters, action buttons.
3. Default content (no `model_id`): card with "Run a simulation to view results".
4. If `model_id` is present: render results (see Simulation Results below).
5. Sidebar dropdown `change` event: navigate to `/workspace/simulations/{selected_model_id}`.
6. **URL-driven model selection**: on initial render, pre-select the dropdown option matching the `model_id` route param.
7. Empty model list: show "Please [create a model](/workspace/models) first."

### Simulation Results (`/workspace/simulations/:model_id`)

1. Fetch `fetchSimResults(model_id)` and render:
   - **Consumption donut chart** (Chart.js `doughnut`): segments PV and Grid; centre label = self-sufficiency %.
   - **PV Generation donut chart**: segments Self-cons. and Grid feed-in; centre label = self-consumption %.
   - **Monthly PV Generation bar chart** (Chart.js `bar`): 12 amber bars, Y axis `"{n} kWh"`.
2. Render two `<input type="date">` fields with defaults `2023-06-19` / `2023-06-24`.
3. Fetch `fetchSimTimeseries(model_id, dateFrom, dateTo)` and render:
   - **Power Profiles line chart** (Chart.js `line`): Load (rose), PV (amber), Battery (teal), Total (indigo); Y axis `"{n} kW"`.
   - **Battery State of Charge line chart** (Chart.js `line`): single teal line; Y axis fixed 0–100, `"{n}%"`.
4. Date input `change` events: re-fetch timeseries and update chart data (`.data.datasets` + `.update()`).
5. No-results state: show "No results found. Run a simulation to get results." in each chart placeholder.

#### Chart.js donut centre label

Chart.js does not render centre labels natively. Use a plugin or CSS overlay:
```typescript
const plugin = {
  id: 'centreLabel',
  afterDraw(chart: Chart) {
    const { ctx, chartArea: { top, right, bottom, left } } = chart;
    ctx.save();
    ctx.font = 'bold 20px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(labelText, (left + right) / 2, (top + bottom) / 2);
    ctx.restore();
  }
};
```

### Finances (`/workspace/finances`)

Same sidebar + content structure as Simulations. The route `/workspace/finances` and `/workspace/finances/:model_id` share one module.

1. Fetch `fetchModels()` and `fetchFinFormData()` on load.
2. Sidebar: model dropdown + all 11 finance input fields (always visible — no advanced toggle in MVP).
3. Pre-populate form fields from `FinData` for the selected model, or from defaults if none saved:
   - `electr_price`: 45, `feed_in_tariff`: 8, `pv_price`: 1500, `battery_price`: 650, `useful_life`: 20, `module_deg`: 0.5, `inflation`: 3, `op_cost`: 1, `down_payment`: 25, `pay_off_rate`: 10, `interest_rate`: 5
4. No-simulation warning + disabled Calculate button if `!model.sim_id`.
5. **Calculate Finances**: show loading overlay → call `submitFinFormData()` → navigate to `/workspace/finances/{model_id}`.
6. Dropdown change: update form fields + navigate to `/workspace/finances/{model_id}` (or `/workspace/finances` if no finance results yet).

#### Form validation (client-side Zod)

Port `FinDataSchema`:
- `electr_price`, `feed_in_tariff`: 0–1000
- `pv_price`, `battery_price`: 0–10,000
- `useful_life`: 0–50
- `module_deg`: 0–100 (exclusive)
- `inflation`, `op_cost`, `down_payment`, `pay_off_rate`, `interest_rate`: 0–100

### Finance Results (`/workspace/finances/:model_id`)

1. Fetch `fetchModels()` and `fetchFinResults(model_id)`.
2. Render:
   - **Model Summary card**: Location, Roof inclination (`{n}°`), Roof orientation (direction name — see mapping in checklist section 7), Consumption, PV peak power, Battery capacity.
   - **KPI card**: 7 rows with formatted values (see checklist section 7 for exact formats).
   - **Performance over Lifetime bar chart** (Chart.js `bar`, grouped + stacked): Investment bar (PV cost + Battery cost stacked, red tones) and Revenue bar (Operation costs negative green + Feed-in revenue medium green + Cost savings light green).
   - **Financial Performance line chart** (Chart.js `line`): Cum. Profit (dark green), Investment (red flat line), Cum. Cash Flow (blue), Loan (orange); X axis individual years; Y axis `"€ {n}"`.
3. No-results state: "No results found. Calculate finances to get results."

#### Roof orientation mapping

```typescript
const ORIENTATION_MAP: Record<number, string> = {
  0: 'South', 45: 'South-West', 90: 'West', 135: 'North-West', 180: 'North',
  [-45]: 'South-East', [-90]: 'East', [-135]: 'North-East',
};
function orientationName(deg: number): string {
  return ORIENTATION_MAP[deg] ?? 'Unknown Orientation';
}
```

---

## Loading Overlay

Implement once, reuse across pages:

```typescript
function showLoadingOverlay(message: string): void {
  const overlay = document.getElementById('loading-overlay')!;
  overlay.querySelector('.loading-message')!.textContent = message;
  overlay.style.display = 'flex';
}

function hideLoadingOverlay(): void {
  document.getElementById('loading-overlay')!.style.display = 'none';
}
```

HTML (in `index.html`, outside `#app`):
```html
<div id="loading-overlay" style="display:none">
  <div class="loading-card">
    <p class="loading-message"></p>
    <div class="spinner"></div>
  </div>
</div>
```

Messages:
- Run Simulation: `"Simulating your energy system ..."`
- Calculate Finances: `"Calculating your system's finances ..."`

---

## Styling Guide

Use CSS custom properties for all colours and spacing. Map the brand colours from the Next.js Tailwind config:

```css
:root {
  --brand-blue: rgb(23, 69, 146);   /* ftblue */
  --blue-100: #dbeafe;
  --blue-300: #93c5fd;
  --blue-500: #3b82f6;
  --rose-500: #f43f5e;
  --amber-500: #f59e0b;
  --teal-500: #14b8a6;
  --indigo-500: #6366f1;
  --green-600: #16a34a;
  --red-500: #ef4444;
  --orange-500: #f97316;
}
```

Key CSS patterns to implement:
- **Sidenav**: fixed left sidebar, flex column, icon + label rows; active link `background-color: var(--blue-100); color: var(--blue-500)`.
- **Cards**: white background, border-radius, box-shadow, a top blue strip.
- **Grid layouts**: CSS Grid (`grid-template-columns`) for the 3-column simulation/finance result layouts.
- **Responsive sidenav**: at narrow viewports (`< 768px`) hide text labels, show icons only.
- **Loading spinner**: CSS `@keyframes` rotation on a `border-top` coloured `div`.
- **Modal dialog**: `<dialog>` element with `::backdrop` pseudo-element for the dimmed overlay.

---

## Caveats and Pitfalls

1. **CORS `allow_origins` wildcard in production**: `backend/src/main.py` currently appends `"*"` to the origins list unconditionally. This is acceptable for development but should be removed in production — set `FRONTEND_BASE_URI` to the exact deployed origin.

2. **Nominatim rate limiting**: Nominatim enforces a 1 req/s rate limit per IP. The browser's `User-Agent` header cannot always be set by `fetch()`; use the `Referer` header or a `User-Agent` query param as fallback. Do not make repeated geocoding calls in tight loops.

3. **`fetch()` timeseries endpoint is POST**: `fetch-sim-timeseries` is a POST with `{ start_time, end_time }` in the JSON body (ISO strings). Start time should be `{date_from}T00:00:00` and end time `{date_to}T23:59:59` (or `T00:00:00` of the day after).

4. **`delete-model` is HTTP DELETE with query params only**: no request body.

5. **Model `sim_id` determines button state**: The model card and simulations sidebar show different buttons depending on whether `model.sim_id` is set (truthy string) or absent/null. Use `!!model.sim_id` for this check.

6. **Power chart date defaults**: default date range is `2023-06-19` to `2023-06-24` — a summer week in 2023. The simulation data covers calendar year 2023; dates outside this range will return empty arrays.

7. **Finance Investment line is flat**: The Investment line in the financial performance chart is rendered as a horizontal flat line (same value for all years). This is intentional — do not attempt to fix it.

8. **Chart.js stacked bar for Performance over Lifetime**: The two "bars" (Investment and Revenue) are actually two `x`-axis categories. Use `type: 'bar'` with `stacked: true` on both axes. Each dataset has an `x` property set to either `'Investment'` or `'Revenue'`.

9. **Chart.js line chart X axis for timeseries**: With potentially thousands of data points, set `animation: false` and use `parsing: false` with pre-formatted data for performance. Only show start and end tick labels: use `ticks.maxTicksLimit: 2`.

10. **SPA history routing**: The browser's `popstate` event fires when the user presses Back/Forward. Register a `window.addEventListener('popstate', ...)` handler that calls the router with the new URL. Without this, Back/Forward will not work correctly.

11. **`<dialog>` browser support**: All modern browsers support native `<dialog>`. The MVP does not require IE or old Safari support.

12. **Vite SPA fallback**: In development Vite handles SPA fallback automatically. In production (nginx, Caddy, etc.) configure the server to serve `index.html` for all routes.

---

## Testing the Vanilla App Against the Mock Backend

For isolated frontend development without a running FastAPI + MongoDB stack, point the vanilla app at the Next.js mock backend:

1. Start the Next.js app: `cd frontend && npm run dev` (port 3000).
2. Set `VITE_BACKEND_BASE_URI=http://localhost:3000/api/mock` in `vanilla/.env.local`.
3. Start the vanilla app: `cd vanilla && npm run dev` (port 5173).

The mock handlers return representative static data for all 9 endpoints. See `nextjs_mvp.md` (Mock Backend section) for handler details.

---

## Migration Phases

The migration is divided into nine phases. Work through them in order — each phase builds on the previous one. Complete all done criteria before starting the next phase.

---

### Phase 1 — Project Scaffolding

**Tasks:**
- Create `vanilla/` directory at the repo root (sibling to `frontend/`).
- Initialise `package.json` with Vite, TypeScript, Chart.js, and Zod dependencies.
- Write `vite.config.ts` with the dev server on port 5173.
- Write `tsconfig.json` (strict mode, ESNext target, bundler module resolution).
- Create `index.html` with a single `<div id="app">`, a `<div id="loading-overlay">`, and the `src/main.ts` script entry point.
- Create `src/styles/global.css` with CSS custom properties for all brand colours (see Styling Guide section).
- Create empty placeholder files for `src/main.ts`, `src/config.ts`, `src/router.ts`, `src/types.ts`, `src/api.ts`, and all page modules under `src/pages/`.

**Done criteria:**
- `npm run dev` in `vanilla/` starts without errors.
- `http://localhost:5173` loads a blank page with no console errors.
- `npm run build` (Vite build) completes without TypeScript or bundler errors.

---

### Phase 2 — Types and API Layer

**Tasks:**
- Port all required types from `frontend/app/utils/definitions.ts` into `src/types.ts`. Omit `FormState` and `EmailFormData` (not needed).
- Write `src/config.ts` exporting `BACKEND_BASE_URI` read from `import.meta.env.VITE_BACKEND_BASE_URI` with a `http://localhost:8000` fallback, and the constant `USER_ID = 'mvp-user'`.
- Implement all 9 `api.ts` fetch wrappers and the `geocodeLocation` Nominatim function (see API Layer section for signatures).
- Create `vanilla/.env.local` with `VITE_BACKEND_BASE_URI=http://localhost:3000/api/mock` for testing against the Next.js mock backend.

**Done criteria:**
- TypeScript compiler reports no errors in `src/types.ts` and `src/api.ts`.
- From the browser console (with the mock backend running on port 3000), calling `import('/src/api.ts').then(m => m.fetchModels())` returns a populated array of models.
- All 9 API functions can be called successfully against the mock backend with no runtime errors.

---

### Phase 3 — Shell, Router, and Sidenav

**Tasks:**
- Implement `src/router.ts`: a route table mapping URL patterns to page render functions, `navigate(path)` that calls `history.pushState` and invokes the matching renderer, and a `popstate` listener for back/forward.
- Implement `src/main.ts`: render the persistent shell HTML (sidenav + `<main id="content">`), register the `[data-link]` click interceptor, register the `popstate` listener, and call the router on initial load.
- Implement sidenav HTML with Ferntree logo link and the three nav links (Models, Simulations, Finances).
- Implement active link highlighting using `window.location.pathname.startsWith(link.dataset.href)`.
- Implement `showLoadingOverlay(message)` and `hideLoadingOverlay()` functions (see Loading Overlay section).
- Add root redirect: if path is `/` navigate to `/workspace`.
- Add a stub renderer for each route that writes a `<p>` placeholder into `<main>`.

**Done criteria:**
- Clicking each sidenav link navigates to the correct URL without a full page reload.
- The browser Back and Forward buttons navigate correctly between visited routes.
- The active sidenav link is highlighted for exact routes and all sub-routes (e.g. `/workspace/simulations/abc` highlights Simulations).
- Navigating to `/` redirects to `/workspace` with no intermediate blank render.
- `showLoadingOverlay('test')` displays the overlay; `hideLoadingOverlay()` removes it.
- Refreshing the page at `/workspace/models` loads the models stub without a 404 (Vite dev server SPA fallback is configured).

---

### Phase 4 — Workspace Home

**Tasks:**
- Implement `src/pages/workspace.ts`: render three workflow step cards (Models, Simulations, Finances) with numbered badges, headings, descriptions, and `[data-link]` hrefs.
- Apply card hover styles (`--blue-100` background → `--blue-300` on hover).
- Render blue `→` arrows between cards (visible on wide screens, hidden on narrow).

**Done criteria:**
- All checklist items in section 2 (Workspace Home) pass.
- Clicking each card navigates to the correct route via the client-side router (no full page reload).
- No data is fetched on this page; no console errors on load.

---

### Phase 5 — Models Page

**Tasks:**
- Implement `src/pages/models.ts`:
  - Fetch `fetchModels()` on load; render empty-state graphic if none, or a card per model.
  - Each model card shows all 6 parameters with icons; location value has a native `title` tooltip.
  - Conditional buttons per card based on `!!model.sim_id` (see checklist section 3).
  - **Delete**: call `deleteModel()`, re-render model list.
  - **Run Simulation**: show loading overlay → call `runSimulation()` → navigate to `/workspace/simulations/{model_id}` on success; hide overlay and re-render on failure.
  - **Create Model button**: disabled with tooltip when `models.length >= 5`.
- Implement Create Model `<dialog>`:
  - All 7 form fields with correct input types, placeholders, and icons.
  - Client-side Zod validation (`ModelDataSchema` rules); show errors inline below each field.
  - On submit: geocode location via `geocodeLocation()`; show error if no result.
  - On success: call `submitModel()`, close dialog, re-render model list without full page reload.
  - Submit button disabled while in-flight.

**Done criteria:**
- All checklist items in section 3 (Models) pass.
- Creating a model with valid data adds it to the list; dialog closes automatically.
- Creating a model with invalid data shows field-level error messages; dialog stays open.
- Entering an unrecognisable location shows the geocoding error message.
- Deleting a model removes it from the list immediately.
- Run Simulation shows the loading overlay until the response arrives, then navigates to simulation results.
- The Create Model button is disabled and shows the tooltip when 5 models exist.

---

### Phase 6 — Simulations Page and Results

**Tasks:**
- Implement `src/pages/simulations.ts` (handles both `/workspace/simulations` and `/workspace/simulations/:model_id`):
  - Fetch `fetchModels()` on load.
  - Render sidebar: model dropdown, selected model parameters (icon + text label), action buttons.
  - Sidebar dropdown `change`: navigate to `/workspace/simulations/{model_id}`.
  - Pre-select dropdown option matching the `model_id` route param on initial render.
  - Empty model list state: "Please [create a model] first."
  - Default content (no `model_id`): "Run a simulation to view results" card.
- Implement simulation results (when `model_id` is present):
  - Fetch `fetchSimResults(model_id)`; show no-results card if null/error.
  - Render Consumption donut chart (Chart.js `doughnut`, segments PV + Grid, centre label = self-sufficiency %).
  - Render PV Generation donut chart (segments Self-cons. + Grid feed-in, centre label = self-consumption %).
  - Render Monthly PV Generation bar chart (12 amber bars, Y axis `"{n} kWh"`).
  - Render two `<input type="date">` fields defaulting to `2023-06-19` / `2023-06-24`.
  - Fetch `fetchSimTimeseries()` with default dates; render Power Profiles line chart (Load, PV, Battery, Total) and Battery SoC line chart (fixed 0–100 Y axis).
  - Date input `change` events: re-fetch timeseries and update charts in place.

**Done criteria:**
- All checklist items in sections 4 and 5 (Simulations) pass.
- Navigating directly to `/workspace/simulations/{model_id}` pre-selects the correct model in the sidebar dropdown.
- Changing the dropdown navigates to the new model's results.
- Changing a date input updates both line charts without a page reload.
- Donut chart centre labels display the correct percentage values.
- No-results state renders correctly when no simulation has been run.

---

### Phase 7 — Finances Page and Results

**Tasks:**
- Implement `src/pages/finances.ts` (handles both `/workspace/finances` and `/workspace/finances/:model_id`):
  - Fetch `fetchModels()` and `fetchFinFormData()` on load.
  - Render sidebar: model dropdown + all 11 finance input fields (always visible).
  - Pre-populate form from saved `FinData` for the selected model, or from defaults if none.
  - Dropdown `change`: update form fields; navigate to `/workspace/finances/{model_id}` if fin results exist, otherwise stay on `/workspace/finances`.
  - No-simulation warning + disabled Calculate button when `!model.sim_id`.
  - View Simulation Results button when `model.sim_id` is set.
  - **Calculate Finances**: client-side Zod validation (`FinDataSchema`); show loading overlay → call `submitFinFormData()` → navigate to `/workspace/finances/{model_id}`.
  - Default content (no `model_id`): "Set up finances to view results" card.
- Implement finance results (when `model_id` is present):
  - Fetch `fetchFinResults(model_id)`; show no-results card if null/error.
  - Render Model Summary card (6 parameters; roof orientation as direction name using `ORIENTATION_MAP`).
  - Render KPI card (7 rows, formatted values — see checklist section 7 for exact formats and `toLocaleString` usage).
  - Render Performance over Lifetime stacked bar chart (Investment bar: PV + Battery cost stacked red tones; Revenue bar: Operation costs negative green + Feed-in medium green + Cost savings light green).
  - Render Financial Performance line chart (Cum. Profit dark green, Investment flat red, Cum. Cash Flow blue, Loan orange; individual year X axis labels; Y axis `"€ {n}"`).

**Done criteria:**
- All checklist items in sections 6 and 7 (Finances) pass.
- Navigating directly to `/workspace/finances/{model_id}` pre-selects the correct model and populates the form with saved values.
- Form pre-populates with defaults for a model with no saved financial data.
- Calculate Finances shows the loading overlay, then navigates to results.
- KPI values use correct `toLocaleString` formatting with explicit `minimumFractionDigits`/`maximumFractionDigits`.
- Bar chart title reads "Performance over Lifetime" (no typo).
- Roof orientation values render as direction names, not raw degree numbers.

---

### Phase 8 — Styling Pass

**Tasks:**
- Review every page against the checklist visual descriptions and align CSS.
- Responsive sidenav: icon-only on screens narrower than 768px; icon + label on wider screens.
- Card top blue decoration strip on all chart/result cards.
- Button colours: blue (Run Simulation), green (View Simulation Results), orange (Go to Finances), red (Delete), blue (Calculate Finances).
- Inline form error messages in red, positioned directly below the relevant field.
- Loading spinner: 64×64 px blue rotating circle.
- Workspace home card hover transition (`--blue-100` → `--blue-300`).
- Desktop layout: blue `→` arrows between workspace home cards; hidden on mobile.
- Chart colours match spec: Load rose, PV amber, Battery teal, Total indigo; Cum. Profit dark green, Investment red, Cum. Cash Flow blue, Loan orange.

**Done criteria:**
- All visual/layout checklist items in sections 1–8 pass.
- Sidenav collapses to icon-only on a narrow viewport (< 768px) with no layout overflow.
- Loading overlay sits above all page content with no z-index conflicts.
- No obviously unstyled or misaligned elements on any page at both desktop (1280px) and mobile (375px) viewport widths.

---

### Phase 9 — Acceptance Testing

**Tasks:**
- Start the vanilla app pointed at the mock backend (`VITE_BACKEND_BASE_URI=http://localhost:3000/api/mock`).
- Step through every checkbox in `nextjs_checklist.md` in order (sections 1–9).
- For each failure: fix the issue, re-verify the specific checkbox, then continue.
- Optionally repeat with the real FastAPI + MongoDB backend to confirm no API contract mismatches.

**Done criteria:**
- Every checkbox in `nextjs_checklist.md` is ticked.
- No console errors during normal user flows (create model, run simulation, calculate finances, navigate between pages).
- Browser Back/Forward works correctly throughout all flows.
- The app loads correctly on a hard refresh at every route (not just `/`).

---

## Acceptance Criteria

Work through every checkbox in `nextjs_checklist.md` against the running vanilla app. All items must pass before the migration is considered complete.

Pay particular attention to:
- Section 1: `startsWith` active link matching (not exact match).
- Section 3: model card button states (sim exists vs. not).
- Section 5: date range picker updates charts without reload; default date is 2023-06-19/2023-06-24.
- Section 7: KPI formatting (`.toLocaleString` with `minimumFractionDigits`/`maximumFractionDigits`).
- Section 7: bar chart title is "Performance over Lifetime" (no typo).
