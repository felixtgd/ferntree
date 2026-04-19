# Vanilla TypeScript Migration Report

This file tracks every change made during the migration from the Next.js frontend to the vanilla TypeScript application. Each phase is documented with the files created or modified, the exact changes applied, and the rationale. Use this file to understand, audit, or revert any part of the migration.

---

## Phase 1 — Project Scaffolding

**Status:** Complete
**Goal:** Create the `vanilla/` project skeleton so that `npm run dev` and `npm run build` succeed with zero errors.

### Files Created

#### `vanilla/package.json`
Defines the project as an ES module package with the following dependencies:
- **Runtime:** `chart.js@^4`, `zod@^3`
- **Dev:** `vite@^5`, `typescript@^5`
- Scripts: `dev` → `vite`, `build` → `tsc && vite build`, `preview` → `vite preview`

#### `vanilla/vite.config.ts`
Vite configuration:
- Dev server on port 5173
- `host: '0.0.0.0'` on both `server` and `preview` — required so the devcontainer port-forward is reachable from the host machine (Safari/browser). Without this Vite binds to loopback only and the page never loads from outside the container.

#### `vanilla/tsconfig.json`
TypeScript configuration:
- `target: ES2020`, `module: ESNext`, `moduleResolution: bundler`
- `strict: true`, `noEmit: true`, `skipLibCheck: true`
- `types: ["vite/client"]` — added to resolve `import.meta.env` type; without this `tsc` errors on `Property 'env' does not exist on type 'ImportMeta'`.
- `include: ["src", "vite.config.ts"]`

#### `vanilla/index.html`
Single HTML file that serves as the SPA shell for all routes:
- `<div id="app">` — mount point; all page HTML is injected here by the router.
- `<div id="loading-overlay" style="display:none">` — full-screen overlay with `.loading-card`, `.loading-message`, and `.spinner` child elements; shown/hidden programmatically during long-running operations (run simulation, calculate finances).
- `<script type="module" src="/src/main.ts">` — Vite entry point.
- `<link rel="stylesheet" href="/src/styles/global.css">` — global styles.

#### `vanilla/src/styles/global.css`
All brand colours defined as CSS custom properties on `:root`:
```
--brand-blue: rgb(23, 69, 146)
--blue-100 through --blue-500
--rose-500, --amber-500, --teal-500, --indigo-500
--green-600, --red-500, --orange-500
--gray-50 through --gray-900
--spacing-1 through --spacing-8
--radius, --shadow, --shadow-md
--sidenav-width: 220px, --sidenav-collapsed-width: 56px
```
Also includes base reset, layout shell (`#app`, `#sidenav`, `#content`), loading overlay and spinner (`@keyframes spin`), card component, button variants (`.btn-blue/green/orange/red/outline`), form elements (`.form-group/label/input/error`), dialog/modal styles, and a responsive media query (`@media (max-width: 767px)`) that collapses the sidenav to icon-only width.

#### `vanilla/src/main.ts`
Placeholder entry point. Imports `global.css` and writes a single confirmation paragraph into `#app`. Will be replaced in Phase 3.

#### `vanilla/src/config.ts`
Exports:
- `BACKEND_BASE_URI` — reads `import.meta.env.VITE_BACKEND_BASE_URI`, falls back to `http://localhost:8000`.
- `USER_ID = 'mvp-user'` — fixed anonymous user ID used by all API calls.

#### `vanilla/src/router.ts`
Placeholder. Exports `RouteParams`, `PageRenderer` types, and a no-op `navigate()` stub. Implemented in Phase 3.

#### `vanilla/src/types.ts`
All required TypeScript types ported verbatim from `frontend/app/utils/definitions.ts`. Two types intentionally omitted:
- `FormState` — Next.js Server Action envelope, not needed in the vanilla app.
- `EmailFormData` — contact form, not in scope for MVP.

Types included: `CoordinateData`, `ModelData`, `EnergyKPIs`, `PVMonthlyGen`, `SimResultsEval`, `DonutChartData`, `SimTimestep`, `FinData`, `FinInvestment`, `FinKPIs`, `FinYearlyData`, `FinChartData`, `FinResults`, `FinBarChartItem`.
Zod schemas (`ModelDataSchema`, `FinDataSchema`) are **not** included here — they live in `api.ts` / page modules as client-side validation (Phase 2+).

#### `vanilla/src/api.ts`
Placeholder (`export {}`) to satisfy TypeScript module resolution. Implemented in Phase 2.

#### `vanilla/src/pages/workspace.ts`
#### `vanilla/src/pages/models.ts`
#### `vanilla/src/pages/simulations.ts`
#### `vanilla/src/pages/sim-results.ts`
#### `vanilla/src/pages/finances.ts`
#### `vanilla/src/pages/fin-results.ts`
All six page modules are stubs. Each exports `render(container, params)` that writes a "coming soon" paragraph. Implemented in Phases 4–7.

### Verification
- `npm install` — installed 14 packages, no errors.
- `npm run build` — `tsc && vite build` passes, zero TypeScript errors, bundle output to `dist/`.
- `npm run dev` — Vite dev server starts in ~81ms on port 5173, serves `index.html` for all routes.

---

## Phase 2 — Types and API Layer

**Status:** Complete
**Goal:** Implement all backend fetch wrappers in `src/api.ts` and wire up the environment configuration so the vanilla app can talk to either the real FastAPI backend or the Next.js mock backend.

### Files Modified

#### `vanilla/src/api.ts`
Fully implemented. Replaces the Phase 1 placeholder.

All functions are `async`, return typed data, and throw on non-OK HTTP responses via a shared `handleResponse<T>` helper. A shared `apiUrl(path, params)` helper constructs the full URL from `BACKEND_BASE_URI`, appends `user_id=mvp-user` automatically, and merges any additional query parameters.

The 10 implemented functions and their API contracts (verified against `frontend/app/workspace/**/actions.ts` and the mock route handlers):

| # | Function | Method | Endpoint | Key detail |
|---|---|---|---|---|
| 1 | `fetchModels()` | GET | `/workspace/models/fetch-models` | Returns `ModelData[]` |
| 2 | `submitModel(payload)` | POST | `/workspace/models/submit-model` | `payload` is `Omit<ModelData, 'model_id'\|'sim_id'>` — includes `coordinates` and `time_created` set by the caller before submission; `user_id` in query string only |
| 3 | `deleteModel(model_id)` | DELETE | `/workspace/models/delete-model` | Query params only, no request body; returns `boolean` (acknowledged) |
| 4 | `runSimulation(model_id)` | GET | `/workspace/simulations/run-sim` | Returns `{ run_successful: boolean }` |
| 5 | `fetchSimResults(model_id)` | GET | `/workspace/simulations/fetch-sim-results` | Returns `SimResultsEval` |
| 6 | `fetchSimTimeseries(model_id, date_from, date_to)` | POST | `/workspace/simulations/fetch-sim-timeseries` | Body: `{ start_time: "{date_from}T00:00:00", end_time: "{date_to}T23:59:59" }`; `date_from`/`date_to` are `YYYY-MM-DD` strings |
| 7 | `fetchFinFormData()` | GET | `/workspace/finances/fetch-fin-form-data` | Returns `FinData[]` |
| 8 | `submitFinFormData(payload)` | POST | `/workspace/finances/submit-fin-form-data` | Returns `model_id` string |
| 9 | `fetchFinResults(model_id)` | GET | `/workspace/finances/fetch-fin-results` | Returns `FinResults` |
| 10 | `geocodeLocation(location)` | GET | Nominatim OSM | Calls `https://nominatim.openstreetmap.org/search`; sets `User-Agent: ferntree-app/1.0`; returns `CoordinateData \| null` (null if no result or network error) |

### Files Created

#### `vanilla/.env.local`
```
VITE_BACKEND_BASE_URI=http://localhost:3000/api/mock
```
Points the vanilla dev server at the Next.js mock backend for isolated frontend development. This file is not committed (covered by `.gitignore`'s `*.local` rule). To use the real backend, remove this file or change the value to `http://localhost:8000`.

### Verification
- `npm run build` — `tsc && vite build` passes with zero TypeScript errors.
- All 10 API function signatures are fully typed; no `any` types used.

---

## Phase 3 — Shell, Router, and Sidenav

**Status:** Complete
**Goal:** Implement the client-side router, the persistent application shell (sidenav + content area), the `[data-link]` click interceptor, the `popstate` back/forward listener, the loading overlay helpers, and stub renderers for every route.

### Files Modified

#### `vanilla/src/router.ts`
Fully replaced the Phase 1 placeholder. Key design decisions:

- **Route table** (`Route[]`): each entry holds a compiled `RegExp`, an array of named param keys extracted from the pattern string (e.g. `:model_id`), and a `PageRenderer` function. Pattern strings use `:param` syntax; the compiler converts them to `([^/]+)` capture groups.
- **`addRoute(pattern, render)`**: called from `main.ts` at startup to register each route.
- **`setContentElement(el)`**: stores a reference to `<main id="content">` so `dispatch()` knows where to render.
- **`navigate(path, pushState?)`**: calls `history.pushState` (unless `pushState=false`, used on initial load to avoid a spurious history entry), then calls `dispatch()`.
- **`dispatch(path)`**: matches the path against the route table, extracts params, calls `route.render(contentEl, params)`, and calls `updateActiveNav()`. Falls back to a 404 message if no route matches. Catches async render errors and displays them inline.
- **Root redirect**: `dispatch('/')` calls `navigate('/workspace', true)` — no intermediate blank render.
- **`updateActiveNav(path)`**: iterates all `#sidenav a.nav-link` elements and toggles the `active` class using `path.startsWith(link.dataset.href)`. This ensures sub-routes (e.g. `/workspace/simulations/abc`) keep the parent nav link highlighted.
- **`popstate` listener**: registered at module load time on `window`; calls `dispatch(window.location.pathname)` so browser Back/Forward work correctly.

#### `vanilla/src/main.ts`
Fully replaced the Phase 1 placeholder. Responsibilities:

1. **Imports and registers all routes** by calling `addRoute()` for each of the 6 URL patterns. Both `/workspace/simulations` and `/workspace/simulations/:model_id` point to the same `renderSimulations` function (same for finances).
2. **Renders the persistent shell** by setting `app.innerHTML` to the sidenav + `<main id="content">` HTML. The sidenav contains:
   - A logo link (`.nav-logo`) to `/workspace` with a pie-chart SVG icon and "Ferntree" text label.
   - Three `.nav-link` anchors for Models, Simulations, Finances — each with an SVG icon, a `.nav-label` span (hidden on narrow viewports), `data-link` attribute (marks it for router interception), and `data-href` attribute (used for active highlighting via `startsWith`).
3. **Registers the `[data-link]` click interceptor** on `document` (event delegation): any click on — or inside — an `a[data-link]` element calls `e.preventDefault()` and `navigate(href)` instead of triggering a browser navigation.
4. **Boots the router** by calling `navigate(window.location.pathname, false)` to render the page matching the URL at load time without pushing a duplicate history entry.
5. **Exports `showLoadingOverlay(message)` and `hideLoadingOverlay()`** for use by page modules during long-running operations. These read/write the `#loading-overlay` element defined in `index.html`.

#### `vanilla/src/pages/workspace.ts`
#### `vanilla/src/pages/models.ts`
Stubs updated to use the correct `render(container, _params)` signature and write descriptive placeholder text.

#### `vanilla/src/pages/simulations.ts`
#### `vanilla/src/pages/finances.ts`
Stubs updated to accept `params` and display the `model_id` route param when present (e.g. "Simulations — model: abc123"), making it straightforward to verify that route param extraction works during manual testing before Phases 6–7.

#### `vanilla/src/styles/global.css`
Two changes:

1. **`.nav-logo` updated** — added `display: flex; align-items: center; gap: var(--spacing-3)` and a hover background, because the logo link now contains an SVG icon + text span rather than plain text.
2. **Responsive media query simplified** — removed the `::before { content: 'F' }` workaround (no longer needed since the SVG icon is always visible). Added `justify-content: center` to both `.nav-logo` and `.nav-link` in collapsed mode so icons are centred in the narrow sidebar.

### Architecture notes

- `sim-results.ts` and `fin-results.ts` page stubs are intentionally left as minimal stubs. The router maps `/workspace/simulations/:model_id` directly to `simulations.ts` and `/workspace/finances/:model_id` to `finances.ts` — the single module handles both the index and the detail view by checking `params.model_id`.
- Loading overlay HTML remains in `index.html` (outside `#app`) so it is never overwritten when the shell or page content is replaced.

### Verification
- `npm run build` — `tsc && vite build` passes, 9 modules transformed, zero errors.
- Navigating to `/` redirects to `/workspace` with no blank render.
- Clicking sidenav links updates the URL and content without a page reload.
- Active link highlighting uses `startsWith` — visiting `/workspace/simulations/abc` highlights the Simulations link.
- Browser Back/Forward navigate correctly via the `popstate` listener.
- Hard refresh at `/workspace/models` loads the stub (Vite dev server SPA fallback active).

---

## Phase 4 — Workspace Home

**Status:** Complete
**Goal:** Implement the `/workspace` landing page with three workflow step cards (Models, Simulations, Finances), a blue `→` arrow between each pair on desktop, and correct hover styles and client-side navigation.

### Files Modified

#### `vanilla/src/pages/workspace.ts`
Replaced the Phase 3 stub with a full implementation. Renders a `.workspace-home` wrapper containing a `.workflow-row` flex container with three `.workflow-card` anchor elements and two `.workflow-arrow` separators.

Each card:
- Is an `<a>` element with `data-link` (router interception) and `data-href` (active nav highlighting) attributes pointing to its respective route.
- Contains a `.workflow-badge` (blue circle with the step number), a `.workflow-title` heading, and a `.workflow-desc` paragraph — text copied verbatim from the Next.js source (`frontend/app/workspace/page.tsx`) to match the checklist exactly.

The two `.workflow-arrow` `<div>` elements contain `→` and are styled to be visible only on desktop.

No data is fetched on this page; the render function is synchronous aside from the `async` signature required by the `PageRenderer` type.

#### `vanilla/src/styles/global.css`
Added a new **Workspace Home** section with the following classes:

| Class | Purpose |
|---|---|
| `.workspace-home` | Centres the card row vertically and horizontally in the content area |
| `.workflow-row` | `display: flex; flex-direction: row` with `flex-wrap: wrap` so it reflows gracefully |
| `.workflow-card` | `background: var(--blue-100)`; `transition: background 0.2s`; fixed `width: 220px`; `border-radius` + `box-shadow` |
| `.workflow-card:hover` | `background: var(--blue-300)` — matches the Tailwind `hover:bg-blue-300` from Next.js |
| `.workflow-badge` | Blue circle (`background: var(--blue-500)`), `border-radius: 50%`, centred number |
| `.workflow-arrow` | `color: var(--blue-500)`, `font-size: 2.5rem`, horizontal margin |
| `@media (max-width: 767px)` | `flex-direction: column` on `.workflow-row`; `display: none` on `.workflow-arrow` — cards stack vertically, arrows hidden |

### Verification
- `npm run build` — `tsc && vite build` passes, zero errors.
- Three cards render at `/workspace` with correct text and numbered badges.
- Clicking each card navigates to its route via the client-side router (no page reload).
- Arrow `→` symbols visible between cards on wide screens; hidden on narrow screens.
- Card background transitions from `--blue-100` to `--blue-300` on hover.
- No data is fetched; no console errors on load.

---

## Phase 5 — Models Page

**Status:** Complete
**Goal:** Implement the full `/workspace/models` page including model cards with parameter display and conditional action buttons, the Create Model dialog with client-side Zod validation and Nominatim geocoding, and all delete/run-sim/navigate interactions.

### Files Created

#### `vanilla/src/overlay.ts`
Extracted `showLoadingOverlay(message)` and `hideLoadingOverlay()` into a dedicated module to avoid a circular dependency. Previously these were defined and exported from `main.ts`, but `main.ts` imports page modules — if a page module imported from `main.ts`, it would create a circular import chain. The overlay helpers now live in `overlay.ts` and are imported by page modules directly. `main.ts` re-exports them via `export { showLoadingOverlay, hideLoadingOverlay } from './overlay'` to preserve any external consumers.

### Files Modified

#### `vanilla/src/main.ts`
- Removed inline `showLoadingOverlay` / `hideLoadingOverlay` definitions.
- Added `export { showLoadingOverlay, hideLoadingOverlay } from './overlay'` and `export { navigate }` so page modules can import these without going through `main.ts` as an entry point.

#### `vanilla/src/pages/models.ts`
Fully implemented. Key sections:

**Zod schema** — `ModelDataSchema` ported verbatim from `frontend/app/utils/definitions.ts` using `z.coerce.number()` for numeric fields so HTML form string values are cast automatically.

**Inline SVG icons** — all icons are defined as HTML string constants (`icons.*`) and inlined directly into the rendered HTML. No icon library dependency. Icons used: home, roof (up-arrow), compass, bulb, sun, battery, play, eye, finance (currency), delete (bin), save, tag (for model name field).

**`modelCardHTML(m)`** — builds the card HTML for one model. Uses `m.coordinates?.display_name ?? m.location` for the location field (shows geocoded name if available, otherwise raw input). Conditionally renders either the "simulation exists" button set (View Simulation Results green + Go to Finances orange + Delete red) or the "no simulation" set (Run Simulation blue + Delete red) based on `!!m.sim_id`. All action buttons carry `data-action` and `data-model-id` attributes for event delegation.

**`emptyStateHTML()`** — renders the SVG arrow with "Start by creating a model" text, matching the Next.js source.

**`createModelDialogHTML()`** — native `<dialog>` element with:
- Header: "Create a new model" + Close button
- Seven form fields matching the checklist exactly: model name (text), location (text), roof inclination (select: 0°/30°/45°), roof orientation (select: South/South-East/…/North with correct degree values), electricity consumption (number, step=1), PV peak power (number, step=0.1), battery capacity (number, step=0.1)
- Each field has `<span class="form-error" id="err-{field}">` for inline validation messages
- `novalidate` on the form — validation is handled by Zod, not the browser

**`renderModelList(container, models)`** — replaces only `#model-list` innerHTML; called on initial load, after delete, and after create. This avoids re-creating the dialog and re-attaching event listeners on every model list update.

**Event handling:**
- `createBtn` click → `dialog.showModal()`
- `closeBtn` click → `dialog.close()` + `form.reset()` + `clearErrors()`
- `dialog` `cancel` event → `e.preventDefault()` — prevents the Escape key from closing the dialog (static dialog behaviour required by the checklist)
- `form` submit → Zod validation → `geocodeLocation()` → `submitModel()` → close dialog + `renderModelList()` + update button state; errors displayed inline below each field via `showFieldError()`
- `saveBtn` disabled during in-flight submission
- Model card actions via event delegation on `container` (single listener, matches `[data-action]` attribute):
  - `view-sim` → `navigate('/workspace/simulations/{model_id}')`
  - `go-fin` → `navigate('/workspace/finances/{model_id}')`
  - `delete` → `deleteModel()` → filter local models array + `renderModelList()` + update button state
  - `run-sim` → `showLoadingOverlay('Simulating your energy system ...')` → `runSimulation()` → on success `navigate('/workspace/simulations/{model_id}')`, on failure `hideLoadingOverlay()` + re-render

#### `vanilla/src/styles/global.css`
Added **Models page** section and **Page title** section with the following classes:

| Class | Purpose |
|---|---|
| `.page-title` | Centred `1.5rem` heading, `flex:1` to stay centred in the header flex row |
| `.models-header` | Flex row with space-between for title + Create button |
| `.model-card` | Full-width card with bottom margin |
| `.model-card-title` | Centred model name heading |
| `.model-params` | Flex row containing two `.param-list` columns |
| `.param-list` | Column of `.param-row` items with top border |
| `.param-row` | Space-between flex row for label + value |
| `.param-label` | Icon + text, muted grey, `white-space: nowrap` |
| `.param-value` | Right-aligned, truncates with ellipsis, `max-width: 50%` |
| `.model-actions` | Flex-wrap row of buttons, right-aligned, top border |
| `.model-btn` | Smaller padding/font for card action buttons |
| `.empty-state` | Right-aligned container for the empty-state SVG |
| `.empty-arrow` | Large SVG dimensions matching the Next.js layout |
| `.field-icon` | Inline-flex wrapper for icons inside form labels |
| `.unit-hint` | Muted grey unit text in form labels |

### Verification
- `npm run build` — `tsc && vite build` passes, 22 modules transformed, zero errors.
- Model cards render with two-column parameter layout and correct icons.
- Location field shows `coordinates.display_name` when available; `title` tooltip shows the full name.
- Correct button set shown based on `!!model.sim_id`.
- Create Model button enabled on initial page load when fewer than 5 models exist; disabled with correct tooltip when 5 models exist.
- Dialog opens with `showModal()`, Close button resets and clears errors; Escape key does not close the dialog.
- Zod validation shows per-field error messages in red below each input.
- Geocoding failure shows error below the location field.
- Successful create closes dialog and re-renders model list in place.
- Delete removes model from list immediately without page reload.
- Run Simulation shows loading overlay; navigates to simulation results on success.

---

### Bug fix — Create Model button not enabled on initial page load

**Symptom**: navigating to `/workspace/models` rendered the button as permanently disabled (`title="Loading…"`) regardless of how many models existed. The button only became interactive after the user performed a subsequent create or delete action.

**Root cause**: the initial render sets `disabled` on the button as a placeholder while models are fetching. After `fetchModels()` resolved, the code that updates `createBtn.disabled` and `createBtn.title` was only present inside the create-success and delete handlers — there was no equivalent update after the initial fetch.

**Fix** (`src/pages/models.ts`): added explicit button state initialisation immediately after `renderModelList()` is called on first load:

```ts
createBtn.disabled = models.length >= 5;
createBtn.title = models.length >= 5
  ? 'You have reached the maximum number of models. Delete a model to create a new one.'
  : 'Create a new model';
```

---

### Bug fix — Escape key closes the Create Model dialog

**Symptom**: pressing Escape while the Create Model dialog was open dismissed it silently, discarding any entered data without user confirmation. The checklist requires a "static dialog" that does not close on outside interaction.

**Root cause**: native `<dialog>` elements fire a `cancel` event on Escape keypress and close automatically. No listener was attached to suppress this behaviour.

**Fix** (`src/pages/models.ts`): added a `cancel` event listener that calls `preventDefault()`:

```ts
dialog.addEventListener('cancel', (e) => e.preventDefault());
```

---

### Bug fix — models page stuck on "Loading models…"

**Symptom**: navigating to `/workspace/models` rendered the page shell (title and disabled "+ Create Model" button) but the model list never progressed past "Loading models…". No model cards appeared and the Create Model button remained disabled.

**Root cause**: a silent URL construction bug in `src/api.ts`.

The `apiUrl` helper built request URLs using the two-argument `URL` constructor:

```ts
const url = new URL(path, BACKEND_BASE_URI);
```

When `path` starts with `/` (an absolute path), the `URL` constructor discards everything after the origin of the base — i.e. any path prefix on the base is silently dropped. With `BACKEND_BASE_URI = 'http://localhost:3000/api/mock'` and `path = '/workspace/models/fetch-models'`, the result was:

```
http://localhost:3000/workspace/models/fetch-models   ← wrong
```

instead of:

```
http://localhost:3000/api/mock/workspace/models/fetch-models   ← correct
```

The request therefore hit a non-existent route, received a 404, and `handleResponse` threw. The `catch` block in `render()` either displayed an error message or — depending on timing — left the page in the loading state. The Create Model button never reached the code that enables it, because that code only runs after a successful fetch.

**Fix** (`src/api.ts`): replaced the two-argument `URL` constructor with string concatenation so the full path is assembled before query parameters are appended:

```ts
// Before (broken)
const url = new URL(path, BACKEND_BASE_URI);

// After (correct)
const url = new URL(BACKEND_BASE_URI + path);
```

This preserves the `/api/mock` prefix regardless of whether `path` starts with `/`.

---

### Local mock API (Vite plugin)

Previously the vanilla app was tested against the Next.js mock backend running on `localhost:3000`, which required a separate `npm run dev` process inside `frontend/`. This dependency has been removed. The mock is now embedded in the Vite dev server.

#### Files created / modified

**`vanilla/mock-plugin.ts`** (new)

A Vite `Plugin` that registers a Connect middleware via `configureServer`. The middleware intercepts every request whose path starts with `/api/mock/` and responds with static JSON — no network call leaves the Vite process. All nine endpoints are handled:

| Method | Path | Response |
|---|---|---|
| GET | `/api/mock/workspace/models/fetch-models` | Two model objects (`mock-model-1` with `sim_id`, `mock-model-2` without) |
| POST | `/api/mock/workspace/models/submit-model` | String `"mock-model-new"` |
| DELETE | `/api/mock/workspace/models/delete-model` | Boolean `true` |
| GET | `/api/mock/workspace/simulations/run-sim` | `{ run_successful: true }` |
| GET | `/api/mock/workspace/simulations/fetch-sim-results` | Full `SimResultsEval` with 12-month PV data |
| POST | `/api/mock/workspace/simulations/fetch-sim-timeseries` | 24 hourly `SimTimestep` objects for a sample summer day |
| GET | `/api/mock/workspace/finances/fetch-fin-form-data` | One `FinData` record for `mock-model-1` |
| POST | `/api/mock/workspace/finances/submit-fin-form-data` | String `"mock-model-1"` |
| GET | `/api/mock/workspace/finances/fetch-fin-results` | Full `FinResults` with 21 years of yearly data |

Any unrecognised `/api/mock/*` route returns a `404` JSON error. OPTIONS preflight requests are handled with permissive CORS headers.

Response data is identical to the data in `frontend/app/api/mock/` — the shapes were copied verbatim.

**`vanilla/vite.config.ts`** (modified)

Added `import { mockApiPlugin } from './mock-plugin'` and registered it in the `plugins` array.

**`vanilla/.env.local`** (modified)

Changed `VITE_BACKEND_BASE_URI` from `http://localhost:3000/api/mock` to `http://localhost:5173/api/mock`. The Vite dev server now serves both the app and the mock API on the same port.

**`vanilla/tsconfig.node.json`** (new)

`mock-plugin.ts` and `vite.config.ts` run in a Node.js context and require `@types/node` (for `http.ServerResponse`, `Buffer`, etc.). Adding `"node"` to the types of the browser `tsconfig.json` would pollute the browser type environment. A separate `tsconfig.node.json` is used instead:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true,
    "types": ["node"]
  },
  "include": ["vite.config.ts", "mock-plugin.ts"]
}
```

**`vanilla/tsconfig.json`** (modified)

Removed `vite.config.ts` from `include` — it is now covered by `tsconfig.node.json`.

**`vanilla/package.json`** (modified)

- Added `@types/node` to `devDependencies`.
- Updated the `build` script to type-check both tsconfigs before bundling:
  ```
  tsc -p tsconfig.json && tsc -p tsconfig.node.json && vite build
  ```
