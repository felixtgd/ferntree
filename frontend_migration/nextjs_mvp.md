# NextJS MVP — Simplification Changes

This document records all changes made to produce the minimal frontend used as the reference for the vanilla JS migration.
It covers two rounds of changes:

1. **Auth strip** — removal of all authentication, login, and user-identity infrastructure
2. **Complexity reduction** — removal of UX polish features that are not strictly necessary for MVP functionality

---

## Round 1: Auth Strip

### Key Design Decision: Anonymous User ID

All 9 backend API endpoints accept `user_id` as a query parameter. Rather than touching the backend, a fixed placeholder `'mvp-user'` is returned by the new `getAnonymousUserId()` function in `helpers.ts`. Every server action that previously called `await getUserID()` (which resolved the real user via NextAuth) now calls the synchronous `getAnonymousUserId()` instead.

### Deleted Files

| File | Reason |
|---|---|
| `frontend/auth.ts` | NextAuth main config (MongoDB adapter, Nodemailer provider, Google/GitHub OAuth) |
| `frontend/auth.config.ts` | Edge-safe NextAuth config used by middleware |
| `frontend/middleware.ts` | Route protection via NextAuth session check |
| `frontend/app/api/auth/[...nextauth]/route.ts` | NextAuth catch-all API route handler |
| `frontend/app/login/page.tsx` | Login page |
| `frontend/app/login/sign-in.tsx` | Sign-in form component |
| `frontend/app/login/provider-button.tsx` | OAuth provider button component |
| `frontend/app/login/actions.ts` | Login server actions |
| `frontend/app/components/contact-form.tsx` | Contact/feedback form (used `sendEmail` and `EmailDataSchema`) |
| `frontend/app/components/sidenav/signout-button.tsx` | Sign-out button component |
| `frontend/app/utils/db.ts` | MongoDB client singleton (only used by NextAuth adapter) |

### Modified Files

#### `frontend/app/page.tsx`
- **Before:** Landing page with marketing content and login CTA.
- **After:** Simple `redirect('/workspace')` — the root now drops straight into the app.

#### `frontend/app/workspace/page.tsx`
- **Before:** Imported `getUser` from `next-auth` and `User` type; rendered a user avatar/welcome card alongside the three workflow step cards.
- **After:** Removed all auth imports and the welcome card. Only the three workflow step cards remain.

#### `frontend/app/components/sidenav/sidenav.tsx`
- **Before:** Imported `signOut` from `@/auth`; rendered a sign-out `<form>` with an inline `'use server'` action and `<SignoutButton>`.
- **After:** Sign-out form and import removed. Sidenav now just renders the logo, nav links, and ferntree icon.

#### `frontend/app/utils/helpers.ts`
- **Removed:** `auth` import from `@/auth`; `Session` and `User` type imports from `next-auth`; `nodemailer` import; `EmailDataSchema` import; `getUser()`, `getUserID()`, `sendEmail()` functions.
- **Added:** `getAnonymousUserId(): string` — returns the fixed string `'mvp-user'`.
- **Kept:** `loadBackendBaseUri()`, `fetchModels()`.

#### `frontend/app/utils/definitions.ts`
- **Removed:** `EmailFormData` type and `EmailDataSchema` Zod schema (were only used by the contact form).

#### `frontend/app/components/button-actions.ts`
- Replaced `getUserID` import and `await getUserID()` call with `getAnonymousUserId` (synchronous).

#### `frontend/app/workspace/models/actions.ts`
- Replaced `getUserID` import and `await getUserID()` call with `getAnonymousUserId`.

#### `frontend/app/workspace/finances/actions.ts`
- Replaced `getUserID` import and both `await getUserID()` calls (`submitFinFormData`, `fetchFinFormData`) with `getAnonymousUserId`.

#### `frontend/app/workspace/simulations/[model_id]/actions.ts`
- Replaced `getUserID` import and both `await getUserID()` calls (`fetchSimResults`, `fetchPowerData`) with `getAnonymousUserId`.

#### `frontend/app/workspace/finances/[model_id]/actions.ts`
- Replaced `getUserID` import and `await getUserID()` call with `getAnonymousUserId`.

#### `frontend/next.config.mjs`
- **Removed:** `images.remotePatterns` block (GitHub and Google avatar hostnames — no longer needed without user avatars).

---

## Round 2: Complexity Reduction

Goal: remove UX polish features not strictly required for MVP functionality, to reduce migration effort and risk.

### Deleted Files

| File | Reason |
|---|---|
| `frontend/app/components/skeletons.tsx` | All skeleton/shimmer loading placeholders removed. Loading is handled by the async server component render — no placeholder needed. |

### Modified Files

#### `frontend/app/workspace/simulations/[model_id]/page.tsx`
- **Removed:** All `<Suspense>` wrappers and skeleton fallbacks.
- **Removed:** `searchParams` prop (no longer needed; date range stored in component state).
- **Added:** Server-side fetch of initial power data (default date range 2023-06-19 to 2023-06-24) passed as prop to `PvPowerChart`.

#### `frontend/app/workspace/finances/[model_id]/page.tsx`
- **Removed:** All `<Suspense>` wrappers and skeleton fallbacks.

#### `frontend/app/workspace/simulations/[model_id]/pv-power-chart.tsx`
- **Converted** from async Server Component to `'use client'` Client Component.
- **Removed:** URL search param reading (`search_params` prop), Zod date validation, `next/navigation` redirect.
- **Added:** `useState` for `dateFrom`/`dateTo` (default Summer range), `chartData`. On date change, calls `fetchPowerData` server action directly and updates chart state in memory.

#### `frontend/app/workspace/simulations/[model_id]/actions.ts`
- **Changed:** `fetchPowerData` signature from `(model_id, date_range: DateRangePickerValue)` to `(model_id, date_from: string, date_to: string)`. Removed `DateRangePickerValue` (Tremor type) dependency.

#### `frontend/app/components/base-comps.tsx`
- **Removed:** `useRouter`, `date-fns/locale`, `DateRangePicker`, `DateRangePickerValue`, `DateRangePickerItem`, `Button` Tremor imports.
- **Removed:** `DropdownMenu*` imports from `components.tsx` and `RiLineChartLine` icon import.
- **Removed:** `useState` import (no longer needed).
- **Replaced `BaseDateRangePicker`:** Tremor `DateRangePicker` with seasonal preset shortcuts replaced by two plain `<input type="date">` fields. New props: `dateFrom`, `dateTo`, `onDateRangeChange`.
- **Simplified `BasePowerLineChart`:** Removed `visibleCategories` state, `handleCategoryToggle`, and the "Select Profiles" `DropdownMenu`. All four profiles (Load, PV, Battery, Total) are always rendered.
- **Simplified `BaseFinLineChart`:** Removed `visibleCategories` state, `handleCategoryToggle`, and the "Select Categories" `DropdownMenu`. All four lines (Cum. Profit, Investment, Cum. Cash Flow, Loan) are always rendered.

#### `frontend/app/workspace/finances/fin_config_form.tsx`
- **Removed:** `showAdvanced` state, `toggleAdvanced` handler, the Advanced toggle `Button`, the collapsible advanced fields section, and the hidden inputs fallback.
- **Removed:** `Flex`, `Button` Tremor imports; `RiArrowDownWideLine`, `RiArrowUpWideLine` icon imports.
- **Changed:** Imports `get_all_input_fields` instead of `get_standard_input_fields` + `get_advanced_input_fields`.
- **Result:** All 11 finance input fields are always visible.

#### `frontend/app/workspace/finances/fin_form_components.tsx`
- **Removed:** `Tooltip` import and its wrapping of field labels. Labels are now plain `<label>` text.
- **Removed:** `tooltip` prop from `NumberInputField`.
- **Removed:** `get_standard_input_fields` and `get_advanced_input_fields` functions.
- **Added:** `get_all_input_fields` — single function returning all 11 fields (standard + former advanced) in sequence.

#### `frontend/app/workspace/models/model-card.tsx`
- **Removed:** `Tooltip`, `RiInformationLine` imports.
- **Replaced:** Location field's info-icon tooltip with a plain `title` attribute on the location `<span>`. The info icon is removed entirely.

#### `frontend/app/workspace/simulations/model_select_form.tsx`
- **Removed:** `useParams`, `useEffect` imports and URL-driven model selection sync (`useEffect` that read `params.model_id` and called `setModelData`).
- **Removed:** `Tooltip` import and all tooltip wrappers on parameter icons.
- **Replaced:** Icon-only parameter rows (with tooltip labels) with icon + visible text label rows.
- **Result:** Sidebar always defaults to the first model in the list; no URL sync.

#### `frontend/app/workspace/finances/[model_id]/fin-kpis.tsx`
- **Removed:** `Tooltip` import and all tooltip wrappers on KPI labels.
- **Replaced:** Each KPI label now uses a native `title` attribute for hover text (browser tooltip).

---

## Round 3: Bug Fixes and Code Quality

A systematic code review identified and fixed 25 issues across the codebase. All fixes listed below were applied; issue M6 (investment flat line) was intentionally left as-is.

### Bug Fixes (HIGH)

| ID | File | Fix |
|---|---|---|
| H1 | `models/model-form.tsx` | `setIsOpen(false)` was called during render (React violation). Wrapped in `useEffect` with `[state, setIsOpen]` deps. |
| H2 | `utils/helpers.ts` | `fetchModels` had no error handling. Added try/catch; returns `[]` on failure. Also added `response.ok` guard. |
| H3 | `finances/actions.ts` | `fetchFinFormData` had no error handling. Added try/catch; returns `[]` on failure. Also added `response.ok` guard. |
| H4 | `finances/fin_config_form.tsx`, `simulations/model_select_form.tsx` | Unsafe `as ModelData` cast after `.find()` replaced with `?? models[0]` fallback. |
| H5 | `finances/fin_config_form.tsx` | `modelData.sim_id !== null` was incorrect for `string \| undefined`; replaced with `!!modelData.sim_id`. |
| H6 | `simulations/[model_id]/actions.ts` | `fetchPowerData` returned `undefined` on error; now explicitly returns `[]`. |

### Code Quality (MEDIUM)

| ID | File | Fix |
|---|---|---|
| M1 | `models/page.tsx`, `model_select_form.tsx`, `fin_config_form.tsx`, `fin_form_components.tsx` | Array index keys replaced with stable IDs (`model_id`, error string). |
| M2 | `fin-kpis.tsx`, `model-summary.tsx` | Numeric values used as React `key` props replaced with stable string literals. |
| M3 | `pv-donut-chart.tsx` | `chart_type: string` narrowed to `'consumption' \| 'generation'` in both function signature and prop type. |
| M4 | `finances/fin_config_form.tsx` | Removed dead `router.refresh()` call after `router.push()`. |
| M5 | `finances/[model_id]/actions.ts` | Error log said `"simResults"` for a fin fetch; corrected to `"finResults"`. |
| M7 | `simulations/[model_id]/actions.ts` | Added comment explaining `cache()` per-request deduplication scope. |
| M8 | `helpers.ts`, `button-actions.ts`, `models/actions.ts`, `simulations/[model_id]/actions.ts`, `finances/actions.ts`, `finances/[model_id]/actions.ts` | Added `response.ok` checks before `.json()` calls; non-2xx responses now throw and are caught. |
| M9 | `models/actions.ts` | Added `User-Agent` header to Nominatim fetch per OSM usage policy. |
| M10 | `models/actions.ts`, `finances/actions.ts` | Removed duplicate `user_id` from POST body; it is already present in the query param. |

### Minor Fixes (LOW)

| ID | File | Fix |
|---|---|---|
| L1 | `fin-bar-chart.tsx` | Typo `"Perfomance"` → `"Performance"`. |
| L2 | `simulations/[model_id]/page.tsx` | Added comment explaining the hard-coded June 2023 default date range. |
| L3 | `layout.tsx` | Added comment explaining the intentional `robots.index:false` / `googleBot.index:true` asymmetry. |
| L4 | `components/components.tsx` | Tooltip arrow colour changed from `fill-gray-900` to `fill-blue-500` to match tooltip background. |
| L5 | `simulations/[model_id]/pv-donut-chart.tsx` | Removed local `classNames()` helper; imports `cx` from `components.tsx` instead. `cx` is now exported from `components.tsx`. |
| L6 | `models/model-form.tsx`, `finances/fin_config_form.tsx` | Migrated `useFormState` from deprecated `react-dom` to `useActionState` from `react`. `useFormStatus` remains in `react-dom`. |
| L7 | `fin-kpis.tsx` | Fixed formatters: `number.toFixed(1).toLocaleString()` (no-op) replaced with `number.toLocaleString(undefined, {minimumFractionDigits:1, maximumFractionDigits:1})`. |
| L8 | `simulations/page.tsx`, `finances/page.tsx` | Removed commented-out `decoration`/`decorationColor` props. |
| L9 | `sidenav/nav-links.tsx` | `pathname === link.href` changed to `pathname.startsWith(link.href)` so active nav highlight persists on sub-routes. |
| L10 | `components/base-comps.tsx` | `max-h-90` (non-standard Tailwind class) changed to `max-h-96`. |

---

## Round 4: Bug Fixes from Manual Testing

Three runtime bugs were discovered during manual end-to-end testing of the Round 3 build. Each required reverting or adjusting a Round 3 change.

### Bug 1 — `'use server'` in `helpers.ts` broke the build

**Root cause:** Round 3 did not add `'use server'` to `helpers.ts`, but a leftover directive was present. The `'use server'` directive requires every export from that module to be `async`. `getAnonymousUserId()` is synchronous, which caused a build-time error.

**Fix:** Removed the `'use server'` directive entirely from `helpers.ts`. The file contains only utility functions called by other server files, not Server Actions invoked directly from the client, so the directive was never correct.

**File:** `frontend/app/utils/helpers.ts`

---

### Bug 2 — `useActionState` does not exist in React 18 (reverted L6)

**Root cause:** L6 migrated `useFormState` to `useActionState` from `react`. `useActionState` is a React 19 API. This project is on **React 18.3.1**, so the import resolved to `undefined` at runtime, crashing both forms.

**Fix:** Reverted both forms back to `useFormState` imported from `react-dom`.

**Files:** `frontend/app/workspace/models/model-form.tsx`, `frontend/app/workspace/finances/fin_config_form.tsx`

---

### Bug 3 — Plain function exports from `'use client'` modules arrive as `undefined` in Server Components (reverted L5)

**Root cause:** L5 exported the `cx` helper from `components.tsx` (a `'use client'` module) and imported it into `pv-donut-chart.tsx` (a Server Component). Next.js serialises `'use client'` module exports for the client bundle; plain (non-async, non-component) function exports are not available when the module is imported from the server side — they arrive as `undefined`.

The same latent issue existed with `moneyFormatter` exported from `base-comps.tsx` (`'use client'`) and used in `fin-kpis.tsx` (Server Component).

**Fix:**
- Reverted L5: removed `cx` export from `components.tsx`; restored local `classNames()` helper directly in `pv-donut-chart.tsx`.
- Defined `moneyFormatter` locally in `fin-kpis.tsx`; the export in `base-comps.tsx` remains for its own internal use only.

**Files:** `frontend/app/workspace/simulations/[model_id]/pv-donut-chart.tsx`, `frontend/app/components/components.tsx`, `frontend/app/workspace/finances/[model_id]/fin-kpis.tsx`

---

## Mock Backend

A mock backend was created as a set of Next.js API route handlers so that the MVP frontend can be tested end-to-end without a running FastAPI server or MongoDB instance.

### Activation

Set `BACKEND_BASE_URI=http://localhost:3000/api/mock` in `frontend/.env.local`. The frontend's `loadBackendBaseUri()` reads this variable and all server actions route to the mock handlers automatically.

### Route Handlers

| File | Endpoint mocked |
|---|---|
| `frontend/app/api/mock/workspace/models/fetch-models/route.ts` | GET `/workspace/models/fetch-models` |
| `frontend/app/api/mock/workspace/models/submit-model/route.ts` | POST `/workspace/models/submit-model` |
| `frontend/app/api/mock/workspace/models/delete-model/route.ts` | DELETE `/workspace/models/delete-model` |
| `frontend/app/api/mock/workspace/simulations/run-sim/route.ts` | GET `/workspace/simulations/run-sim` |
| `frontend/app/api/mock/workspace/simulations/fetch-sim-results/route.ts` | GET `/workspace/simulations/fetch-sim-results` |
| `frontend/app/api/mock/workspace/simulations/fetch-sim-timeseries/route.ts` | POST `/workspace/simulations/fetch-sim-timeseries` |
| `frontend/app/api/mock/workspace/finances/fetch-fin-form-data/route.ts` | GET `/workspace/finances/fetch-fin-form-data` |
| `frontend/app/api/mock/workspace/finances/submit-fin-form-data/route.ts` | POST `/workspace/finances/submit-fin-form-data` |
| `frontend/app/api/mock/workspace/finances/fetch-fin-results/route.ts` | GET `/workspace/finances/fetch-fin-results` |

### Behaviour

- All mutation endpoints (submit-model, delete-model, run-sim, submit-fin-form-data) return immediate success responses.
- Data is static and not persisted between page refreshes.
- `fetch-models` returns a single pre-seeded model with a `sim_id` already set so all pages render populated.
- `fetch-sim-results` and `fetch-sim-timeseries` return representative numeric data sufficient to render all charts.
- `fetch-fin-results` returns representative financial KPIs and yearly data.

---

## Verification

`npm run lint` in `frontend/` reports no ESLint warnings or errors after all changes.
