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
