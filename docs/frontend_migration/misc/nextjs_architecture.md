# NextJS Frontend Architecture — Ferntree

This document is a comprehensive analysis of the existing NextJS frontend, produced as the foundation for planning a migration to vanilla TypeScript, HTML and CSS.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Pages and Routes](#2-pages-and-routes)
3. [Layouts](#3-layouts)
4. [Components](#4-components)
5. [API Calls](#5-api-calls)
6. [State Management](#6-state-management)
7. [Authentication](#7-authentication)
8. [Routing and Navigation](#8-routing-and-navigation)
9. [Styling](#9-styling)
10. [Forms and Validation](#10-forms-and-validation)
11. [Data Fetching Patterns](#11-data-fetching-patterns)
12. [External Libraries](#12-external-libraries)
13. [TypeScript Types](#13-typescript-types)
14. [Configuration Files](#14-configuration-files)
15. [Environment Variables](#15-environment-variables)
16. [Key Architecture Decisions](#16-key-architecture-decisions)

---

## 1. Project Structure

```
frontend/
├── .eslintrc.json
├── next.config.mjs
├── package.json
├── postcss.config.mjs
├── tailwind.config.ts
├── tsconfig.json
├── vercel.json
├── auth.ts                               # NextAuth full config (with DB adapter)
├── auth.config.ts                        # NextAuth base config (edge-safe)
├── middleware.ts                         # Route protection middleware
├── public/
│   ├── favicon.ico
│   └── ferntree.png
└── app/
    ├── globals.css
    ├── layout.tsx                        # Root layout
    ├── page.tsx                          # Landing page (/)
    ├── api/
    │   └── [...nextauth]/
    │       └── route.ts                  # NextAuth API handler
    ├── login/
    │   ├── page.tsx
    │   ├── sign-in.tsx
    │   ├── provider-button.tsx
    │   └── actions.ts
    ├── workspace/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── models/
    │   │   ├── page.tsx
    │   │   ├── actions.ts
    │   │   ├── model-card.tsx
    │   │   ├── model-form-dialog.tsx
    │   │   └── model-form.tsx
    │   ├── simulations/
    │   │   ├── layout.tsx
    │   │   ├── page.tsx
    │   │   ├── model_select_card.tsx
    │   │   ├── model_select_form.tsx
    │   │   └── [model_id]/
    │   │       ├── page.tsx
    │   │       ├── actions.ts
    │   │       ├── pv-donut-chart.tsx
    │   │       ├── pv-gen-bar-chart.tsx
    │   │       └── pv-power-chart.tsx
    │   └── finances/
    │       ├── layout.tsx
    │       ├── page.tsx
    │       ├── actions.ts
    │       ├── fin_config_card.tsx
    │       ├── fin_config_form.tsx
    │       ├── fin_form_components.tsx
    │       └── [model_id]/
    │           ├── page.tsx
    │           ├── actions.ts
    │           ├── model-summary.tsx
    │           ├── fin-kpis.tsx
    │           ├── fin-bar-chart.tsx
    │           └── fin-line-chart.tsx
    ├── components/
    │   ├── base-comps.tsx
    │   ├── button-actions.ts
    │   ├── buttons.tsx
    │   ├── components.tsx
    │   ├── contact-form.tsx
    │   ├── loading-screen.tsx
    │   ├── skeletons.tsx
    │   └── sidenav/
    │       ├── sidenav.tsx
    │       ├── nav-links.tsx
    │       ├── ferntree-logo.tsx
    │       └── signout-button.tsx
    └── utils/
        ├── db.ts
        ├── definitions.ts
        └── helpers.ts
```

---

## 2. Pages and Routes

| Route | File | Purpose |
|---|---|---|
| `/` | `app/page.tsx` | Public landing page. Marketing content, "Get Started"/"Log in" CTAs, contact/feedback form, footer with GitHub link. No authentication required. |
| `/login` | `app/login/page.tsx` | Authentication page. Renders email sign-in form and GitHub/Google OAuth buttons. Authenticated users are redirected away by middleware. |
| `/workspace` | `app/workspace/page.tsx` | Workspace home. Displays the current user's avatar and name with a welcome message, and three workflow step cards linking to Models → Simulations → Finances. |
| `/workspace/models` | `app/workspace/models/page.tsx` | Lists all models belonging to the current user. Shows an empty-state graphic if none exist. Renders a `ModelCard` for each model and a "Create Model" button (capped at 5 models). |
| `/workspace/simulations` | `app/workspace/simulations/page.tsx` | Index placeholder. Shows a "Run a simulation to view results" prompt. The sidebar allows model selection and triggering a simulation run. |
| `/workspace/simulations/[model_id]` | `app/workspace/simulations/[model_id]/page.tsx` | Simulation results dashboard for a given model. Shows: energy consumption/generation donut charts, monthly PV generation bar chart, and an interactive power time-series line chart with a date-range picker. |
| `/workspace/finances` | `app/workspace/finances/page.tsx` | Index placeholder. Shows "Set up finances to view results". The sidebar contains the financial parameter configuration form. |
| `/workspace/finances/[model_id]` | `app/workspace/finances/[model_id]/page.tsx` | Financial analysis dashboard for a given model. Shows: model parameter summary card, financial KPI list, investment vs. revenue bar chart, and a cumulative financial performance line chart. |

---

## 3. Layouts

Layouts wrap their child routes and persist across navigation within their segment.

| Layout File | Route Segment | What It Adds |
|---|---|---|
| `app/layout.tsx` | All routes | Applies Inter font, global CSS, and root HTML metadata. |
| `app/workspace/layout.tsx` | `/workspace/**` | Renders `SideNav` on the left beside page content. |
| `app/workspace/simulations/layout.tsx` | `/workspace/simulations/**` | Two-column grid: `ModelSelection` sidebar (col-1) + children (col-4). |
| `app/workspace/finances/layout.tsx` | `/workspace/finances/**` | Two-column grid: `FinanceConfig` sidebar (col-1) + children (col-4). |

---

## 4. Components

### 4.1 Shared Components (`app/components/`)

#### Charts and Cards (`base-comps.tsx`) — Client Component

| Component | Purpose |
|---|---|
| `BaseCard` | A card with a top blue decoration strip, centered title, and a child slot. Used as the wrapper for every chart card. |
| `BaseDonutChart` | Tremor `DonutChart` with kWh formatter. Used for energy consumption and generation split charts. |
| `BasePvBarChart` | Tremor `BarChart` (amber color) showing monthly PV generation. |
| `BaseFinBarChart` | Tremor stacked `BarChart` for investment vs. revenue breakdown. |
| `BaseDateRangePicker` | Tremor `DateRangePicker` with four preset seasonal date ranges. On change it updates URL search params via `router.replace`. |
| `BasePowerLineChart` | Two stacked `LineChart`s — power profiles (Load, PV, Battery, Total) and battery State of Charge — with a dropdown to toggle which categories are visible. |
| `BaseFinLineChart` | `LineChart` for cumulative financial performance over time (Profit, Cash Flow, Loan) with a category toggle dropdown. |

#### Action Buttons (`buttons.tsx`) — Client Component

| Component | Action Triggered | Used In |
|---|---|---|
| `DeleteModelButton` | Calls `deleteModel` server action; revalidates models page. | `model-card.tsx` |
| `RunSimButton` | Calls `runSimulation` server action; shows `LoadingScreen` while pending; redirects to simulation results on success. | `model-card.tsx`, `model_select_form.tsx`, `fin_config_form.tsx` |
| `ViewSimButton` | Calls `viewResults` action; navigates to `/workspace/simulations/[id]`. | `model-card.tsx`, `model_select_form.tsx`, `fin_config_form.tsx` |
| `GoToFinButton` | Calls `goToFin` action; navigates to `/workspace/finances/[id]`. | `model-card.tsx`, `model_select_form.tsx` |

#### UI Primitives (`components.tsx`) — Client Component

| Component | Based On | Purpose |
|---|---|---|
| `Tooltip` | Radix UI `@radix-ui/react-tooltip` | Blue-styled tooltip with animated slide-in. |
| `DropdownMenu*` | Radix UI `@radix-ui/react-dropdown-menu` | Full dropdown menu primitive suite (trigger, content, checkbox items, etc.) — used in chart category toggles. |
| `Table*` | Custom | Full table component suite (defined but not actively used in current pages). |

#### Other Shared Components

| Component | File | Purpose |
|---|---|---|
| `ContactForm` | `contact-form.tsx` | Contact/feedback form with name, email, category, and message fields. Uses `useOptimistic` for instant "submitted" feedback. DOMPurify sanitizes inputs. |
| `LoadingScreen` | `loading-screen.tsx` | Fixed full-screen black overlay with spinner and message. Shown while a simulation run is in progress. |
| `BaseSkeleton`, `DonutSkeleton`, `BarSkeleton`, `FinKpiSkeleton`, `FinBarSkeleton`, `LineChartSkeleton` | `skeletons.tsx` | Shimmer-animation loading placeholders for each chart type. Used as `Suspense` fallbacks. |

### 4.2 SideNav Components (`app/components/sidenav/`)

| Component | Type | Purpose |
|---|---|---|
| `SideNav` | Server | Outer nav shell: logo link, `NavLinks`, sign-out button. Sign-out is an inline server action calling NextAuth `signOut()`. |
| `NavLinks` | Client | Three nav links (Models / Simulations / Finances). Uses `usePathname` to highlight the active link. |
| `FerntreeLogo` | Server | Renders the "Ferntree" brand text. |
| `SignoutButton` | Client | A button that submits the sign-out form. |

### 4.3 Login Components (`app/login/`)

| Component | Type | Purpose |
|---|---|---|
| `SignInProvider` | Client | Form with a hidden provider name field and a `ProviderButton`. Submits `signInAction`. |
| `SignInEmail` | Client | Email input form with `useOptimistic` for immediate "check your email" feedback after submission. |
| `ProviderButton` | Client | Button with an OAuth provider icon (GitHub via `RiGithubFill`, Google via `RiGoogleFill`). |
| `EmailSignInButton` | Client | Submit button with a mail icon for the email sign-in form. |

### 4.4 Models Components (`app/workspace/models/`)

| Component | Type | Purpose |
|---|---|---|
| `ModelCard` | Server (async) | Card displaying all parameters of one model. Shows conditional action buttons depending on whether a simulation exists. |
| `ModelFormDialog` | Client | "Create Model" button that opens a Tremor `Dialog` containing `ModelForm`. Disabled when 5 models already exist. |
| `ModelForm` | Client | Model creation form. Fields: name, location, roof inclination, azimuth, electricity consumption, peak power, battery capacity. Validates via `useFormState(submitModel)`. |

### 4.5 Simulations Components (`app/workspace/simulations/`)

| Component | Type | Purpose |
|---|---|---|
| `ModelSelection` | Server (async) | Fetches models list, wraps `ModelSelectForm` in a card. Used in the simulations layout sidebar. |
| `ModelSelectForm` | Client | Model selector dropdown with model parameter list and Run/View/Finance action buttons. Syncs selected model with the current URL via `useParams`. |
| `PvDonutChart` | Server (async) | Fetches simulation results; renders two donut charts showing energy consumption split and generation split. |
| `PvGenBarChart` | Server (async) | Fetches simulation results; renders a monthly PV generation bar chart. |
| `PvPowerChart` | Server (async) | Reads date range from URL `searchParams`, validates with Zod, fetches timeseries data; renders the date-range picker and power line charts. |

### 4.6 Finances Components (`app/workspace/finances/`)

| Component | Type | Purpose |
|---|---|---|
| `FinanceConfig` | Server (async) | Fetches models and saved financial form data; renders `FinanceConfigForm` or a prompt to run a simulation first. Used in the finances layout sidebar. |
| `FinanceConfigForm` | Client | Financial parameter form with standard and collapsible advanced fields. Uses `useFormState(submitFinFormData)`. Redirects to results on successful submit. |
| `NumberInputField` | Client | Labelled `NumberInput` with tooltip and inline validation error display. |
| `SubmitButton` (finances) | Client | Submit button disabled when no simulation exists or form is pending; shows `LoadingScreen` while pending. |
| `ModelSummary` | Server (async) | Fetches models and displays the current model's parameters in a `BaseCard`. |
| `FinKpis` | Server (async) | Fetches financial results; renders the financial KPI list (total investment, cumulative profit, break-even year, LCOE, ROI, loan details, etc.). |
| `FinBarChart` | Server (async) | Fetches financial results; renders the investment vs. revenue breakdown bar chart. |
| `FinLineChart` | Server (async) | Fetches financial results; renders the cumulative financial performance line chart over the system's lifetime. |

---

## 5. API Calls

All calls to the backend are made **server-side** (inside Server Components or Server Actions). The browser never directly contacts the FastAPI backend. The base URL is read from `process.env.BACKEND_BASE_URI`.

### 5.1 Backend API Calls (FastAPI)

| # | Endpoint | Method | Query Params | Request Body | Response | Made In |
|---|---|---|---|---|---|---|
| 1 | `/workspace/models/fetch-models` | GET | `user_id` | — | `ModelData[]` | `utils/helpers.ts` → `fetchModels()` |
| 2 | `/workspace/models/submit-model` | POST | `user_id` | `{ model_name, location, roof_incl, roof_azimuth, electr_cons, peak_power, battery_cap, user_id, coordinates: { lat, lon, display_name }, time_created }` | `string` (model_id) | `models/actions.ts` → `submitModel()` |
| 3 | `/workspace/models/delete-model` | DELETE | `user_id`, `model_id` | — | `boolean` (acknowledged) | `components/button-actions.ts` → `deleteModel()` |
| 4 | `/workspace/simulations/run-sim` | GET | `user_id`, `model_id` | — | `{ run_successful: boolean }` | `components/button-actions.ts` → `runSimulation()` |
| 5 | `/workspace/simulations/fetch-sim-results` | GET | `user_id`, `model_id` | — | `SimResultsEval` | `simulations/[model_id]/actions.ts` → `fetchSimResults()` |
| 6 | `/workspace/simulations/fetch-sim-timeseries` | POST | `user_id`, `model_id` | `{ start_time: ISO string, end_time: ISO string }` | `SimTimestep[]` | `simulations/[model_id]/actions.ts` → `fetchPowerData()` |
| 7 | `/workspace/finances/submit-fin-form-data` | POST | `user_id` | `{ model_id, electr_price, feed_in_tariff, pv_price, battery_price, useful_life, module_deg, inflation, op_cost, down_payment, pay_off_rate, interest_rate, user_id }` | `string` (model_id) | `finances/actions.ts` → `submitFinFormData()` |
| 8 | `/workspace/finances/fetch-fin-form-data` | GET | `user_id` | — | `FinData[]` | `finances/actions.ts` → `fetchFinFormData()` |
| 9 | `/workspace/finances/fetch-fin-results` | GET | `user_id`, `model_id` | — | `FinResults` | `finances/[model_id]/actions.ts` → `fetchFinResults()` |

### 5.2 External Third-Party API Calls

| # | Endpoint | Method | Query Params | Response | Made In |
|---|---|---|---|---|---|
| 10 | `https://nominatim.openstreetmap.org/search` | GET | `q={location}`, `format=json`, `limit=1` | `[{ lat, lon, display_name }]` | `models/actions.ts` → `getLocationCoordinates()` |

> **Note on geocoding**: When a user creates a model, the location string they enter is geocoded via OpenStreetMap Nominatim. The resulting `{ lat, lon, display_name }` is stored alongside the model in MongoDB and then sent to the backend along with the model data.

### 5.3 Authentication API (Internal)

- `app/api/[...nextauth]/route.ts` — catch-all handler for all NextAuth GET/POST endpoints (OAuth callbacks, magic-link verification, CSRF token, session management). This is not a direct fetch call from application code; it is handled internally by NextAuth.

---

## 6. State Management

There is no global state management library. All state is React-local or URL-based.

| Mechanism | Location | Purpose |
|---|---|---|
| `useState` | `model-form-dialog.tsx` | Dialog open/closed |
| `useState` | `model-form.tsx` | Form field values |
| `useState` | `model_select_form.tsx` | Selected model |
| `useState` | `fin_config_form.tsx` | Selected model, form field values, `showAdvanced` toggle |
| `useState` | `contact-form.tsx` | Form field values, `isSubmitted` flag |
| `useState` | `buttons.tsx` | `isLoading` for simulation spinner |
| `useState` | `base-comps.tsx` | `selectedDateRange`, `visibleCategories` for chart controls |
| `useFormState` | `model-form.tsx`, `fin_config_form.tsx`, `contact-form.tsx` | Server action response + validation errors |
| `useFormStatus` | Submit buttons in forms | Pending state to disable submit during in-flight request |
| `useOptimistic` | `sign-in.tsx`, `contact-form.tsx` | Optimistic UI update before server confirms |
| `useParams` | `model_select_form.tsx`, `fin_config_form.tsx` | Read `model_id` from current URL |
| `usePathname` | `nav-links.tsx` | Active link highlighting |
| `useRouter` | `buttons.tsx`, `fin_config_form.tsx`, `base-comps.tsx` | Programmatic navigation and URL param updates |
| `useEffect` | `model_select_form.tsx`, `fin_config_form.tsx` | Sync component state with URL on mount; redirect after successful form submit |
| React `cache()` | `helpers.ts` (`fetchModels`), `simulations/actions.ts` (`fetchSimResults`) | Deduplicate identical server-side fetches within a single render pass |
| URL search params | `pv-power-chart.tsx` + `BaseDateRangePicker` | Date range state persisted in URL (`?dateFrom=&dateTo=`) for bookmarkable chart state |

---

## 7. Authentication

The app uses **Auth.js v5 (NextAuth v5 beta)** with JWT sessions and three sign-in methods.

### Sign-In Methods

| Method | Provider | Flow |
|---|---|---|
| GitHub OAuth | `authConfig` (GitHub provider) | Click button → `signInAction` calls `signIn('github')` → OAuth redirect → session stored in MongoDB via adapter |
| Google OAuth | `authConfig` (Google provider) | Click button → `signInAction` calls `signIn('google')` → OAuth redirect → session stored in MongoDB via adapter |
| Magic link (email) | `auth.ts` (Nodemailer provider) | Enter email → `signInAction` calls `signIn('nodemailer', formData)` → NextAuth sends one-time link via SMTP → user clicks link → session created |

### Sign-Out

An inline server action in `SideNav` calls `signOut()` directly — no client-side redirect needed.

### Route Protection

- `middleware.ts` runs on every request (except static assets).
- The `authorized` callback in `auth.config.ts` redirects unauthenticated users from `/workspace/**` to `/login`.
- Authenticated users visiting `/login` are redirected to `/workspace`.
- `getUser()` and `getUserID()` in `helpers.ts` throw if called without a valid session, providing a server-side guard in data-fetching code.

### Auth Configuration Split

| File | Runtime | Purpose |
|---|---|---|
| `auth.config.ts` | Edge-safe | GitHub/Google providers, custom sign-in page, `authorized`/`jwt`/`session` callbacks |
| `auth.ts` | Node.js | Imports `authConfig`, adds `MongoDBAdapter` and `Nodemailer` provider |
| `middleware.ts` | Edge | Applies the `authorized` callback; uses only `auth.config.ts` (no Node.js-only modules) |
| `app/api/[...nextauth]/route.ts` | Node.js | Handles all NextAuth HTTP endpoints; explicitly sets `runtime = "nodejs"` |

---

## 8. Routing and Navigation

- **Router type**: Next.js App Router (`app/` directory). No Pages Router (`pages/`) is used.
- **API routes**: One catch-all handler at `app/api/[...nextauth]/route.ts`.
- **Dynamic segments**: `[model_id]` in simulations and finances routes.
- **No route groups, parallel routes, or intercepting routes**.

### Navigation Mechanisms

| Mechanism | Where Used | When |
|---|---|---|
| `<Link href="...">` | `nav-links.tsx`, landing page, workspace home | Declarative client-side navigation |
| `redirect()` from `next/navigation` | Server Actions (`submitModel`, `runSimulation`, etc.) | Imperative redirect after a mutation |
| `router.push()` | `fin_config_form.tsx` | Navigate to finance results after successful form submit |
| `router.replace()` | `base-comps.tsx` (`BaseDateRangePicker`) | Update URL search params without adding a history entry |
| `router.refresh()` | `buttons.tsx` (`RunSimButton`) | Trigger re-fetch of server data after simulation completes |

### Cache Invalidation

`revalidatePath()` is called after mutations to clear the Next.js data cache:
- `revalidatePath('/workspace/models')` — after model creation or deletion
- `revalidatePath('/workspace/simulations')` — after running a simulation

### URL Search Params

The power chart date range is stored in the URL as `?dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD`. The server component `PvPowerChart` reads `searchParams`, the client component `BaseDateRangePicker` writes them. This makes the chart state bookmarkable and shareable.

---

## 9. Styling

| Approach | Details |
|---|---|
| **Tailwind CSS v3** | Primary styling mechanism. All layout, spacing, colour, and typography use Tailwind utility classes. No CSS modules or styled-components. |
| **Global CSS** (`globals.css`) | Imports Tailwind base/components/utilities. Sets CSS variables for foreground/background. Defines a white-to-light-blue vertical gradient on `body`. Removes number input spinners globally. |
| **Tremor design tokens** | Extensive custom colour tokens (`tremor.brand.*`, `tremor.background.*`, dark mode variants), box shadows, border radii, and font sizes configured in `tailwind.config.ts`. |
| **Brand colour** | `ftblue: 'rgb(23, 69, 146)'` defined in Tailwind config. Tremor `blue-500` is used pervasively throughout. |
| **Fonts** | Inter (Google Font, latin subset) via `next/font/google` in the root layout. |
| **Dark mode** | Configured as `class`-based in Tailwind config. Tremor dark mode tokens are defined, but no dark mode toggle exists in the UI — dark mode is not actively used. |
| **Custom animations** | `hide`, `slideDownAndFade`, `slideLeftAndFade`, `slideUpAndFade`, `slideRightAndFade` keyframes in `tailwind.config.ts` for tooltip and dropdown entrance animations. |
| **Tailwind safelist** | All colour scale classes (50–950) with `bg-*`, `text-*`, `border-*`, `ring-*`, `stroke-*`, `fill-*` patterns are safelisted to prevent purging of dynamically constructed Tremor class names. |
| **Plugins** | `@headlessui/tailwindcss` (for `ui-selected`/`ui-open` variants), `@tailwindcss/forms` (opinionated base form styles). |
| **Class merging utility** | `clsx` + `tailwind-merge` combined in a `cx()` helper in `components.tsx` for conflict-free dynamic class composition. |

---

## 10. Forms and Validation

### Form Approach

Native HTML `<form>` elements with React Server Actions (`action={serverAction}`). No form library (no React Hook Form, no Formik).

| Hook | Source | Used For |
|---|---|---|
| `useFormState` | `react-dom` | Connects a form to a server action; surfaces validation errors returned from the action. |
| `useFormStatus` | `react-dom` | Detects the pending state of a parent form submission to disable the submit button. |
| `useOptimistic` | React 18 | Provides immediate UI feedback before the server responds (login page, contact form). |

### Validation: Zod (server-side only)

All validation happens inside Server Actions. There is no client-side validation library.

| Schema | Fields |
|---|---|
| `ModelDataSchema` | `model_name` (1–100 chars), `location` (1–100 chars), `roof_incl` (0–90°), `roof_azimuth` (−180–180°), `electr_cons` (0–100,000 kWh), `peak_power` (0–100,000 kWp), `battery_cap` (0–100,000 kWh) |
| `FinDataSchema` | `model_id`, `electr_price`, `feed_in_tariff`, `pv_price`, `battery_price`, `useful_life`, `module_deg`, `inflation`, `op_cost`, `down_payment`, `pay_off_rate`, `interest_rate` — all coerced numbers with min/max bounds |
| `EmailDataSchema` | `name` (1–100), `email` (valid email, max 100), `category` (1–100), `message` (1–1000) |
| Inline date range schema | `{ from: z.date(), to: z.date() }` — validates URL search params in `pv-power-chart.tsx` |

Validation errors are rendered inline below each field using `aria-live="polite"` and `aria-atomic="true"`.

### Input Sanitization

`DOMPurify.sanitize()` is applied to all contact form field values before state updates, guarding against XSS.

### Finance Form: Progressive Disclosure

The finance configuration form has two tiers:
- **Standard fields** (always visible): electricity price, feed-in tariff, PV price, battery price, useful life.
- **Advanced fields** (hidden behind a toggle): module degradation, inflation, operation cost, down payment, payoff rate, interest rate.

Hidden inputs ensure advanced field values are submitted even when the section is collapsed.

---

## 11. Data Fetching Patterns

| Pattern | Where Used | Notes |
|---|---|---|
| **Async Server Components** | Most data-displaying components (charts, cards, model lists) | Components `await` data directly without `useEffect` or client-side loading state. |
| **`Suspense` + skeleton fallbacks** | `simulations/[model_id]/page.tsx`, `finances/[model_id]/page.tsx` | Each chart component is individually wrapped in `<Suspense key={params.model_id} fallback={<Skeleton/>}>`. The `key` prop forces re-render when `model_id` changes. |
| **React `cache()`** | `fetchModels()`, `fetchSimResults()` | Deduplicates identical fetches within a single render pass. `fetchModels` is called by the models page, simulations sidebar, finances sidebar, and model summary — caching prevents redundant HTTP calls. |
| **Server Actions (mutations)** | `submitModel`, `deleteModel`, `runSimulation`, `submitFinFormData` | Validate → call backend API → `revalidatePath()` → return `FormState`. |
| **URL search params as state** | Power chart date range | Stored in the URL; server component reads them; client date-picker updates them via `router.replace`. |
| **No `getServerSideProps` / `getStaticProps`** | — | App Router only; these Pages Router patterns are not used. |
| **No SWR / React Query** | — | No client-side data fetching library. All fetching is server-side. |

---

## 12. External Libraries

### Production Dependencies

| Package | Version | Role |
|---|---|---|
| `next` | ^14.2.35 | Core framework — App Router, Server Components, Server Actions, `next/image`, `next/font`, `next/navigation`, `next/cache` |
| `react` + `react-dom` | ^18 | Component model, hooks, `Suspense`, `useOptimistic`, `useFormState`, `useFormStatus` |
| `next-auth` | ^5.0.0-beta.30 | Authentication — GitHub OAuth, Google OAuth, Nodemailer magic-link email, JWT sessions, route-protection middleware |
| `@auth/mongodb-adapter` | ^3.4.2 | Persists NextAuth sessions, accounts, and users to MongoDB |
| `mongodb` | ^6.8.0 | MongoDB Node.js driver — used for the DB client singleton in `utils/db.ts` |
| `@tremor/react` | ^3.17.2 | Primary UI component library — `Card`, `Button`, `Dialog`, `DonutChart`, `BarChart`, `LineChart`, `DateRangePicker`, `NumberInput`, `TextInput`, `Textarea`, `Select`, `List` |
| `@headlessui/react` | ^2.0.4 | Headless accessible UI primitives (Tremor dependency; also provides animation hooks) |
| `@headlessui/tailwindcss` | ^0.2.1 | Tailwind plugin for `ui-selected` and `ui-open` state variants |
| `@heroicons/react` | ^2.1.3 | Icon library (imported but largely superseded by Remix Icon) |
| `@radix-ui/react-tooltip` | ^1.1.3 | Tooltip primitive used in the custom `Tooltip` component |
| `@radix-ui/react-dropdown-menu` | ^2.1.2 | Dropdown menu primitives used in chart category toggles |
| `@radix-ui/react-checkbox` | ^1.1.2 | Listed dependency (likely transitive; not directly referenced in source) |
| `@remixicon/react` | ^4.5.0 | Primary icon library — used throughout for action icons, nav icons, auth provider icons |
| `clsx` | ^2.1.0 | Conditional class name composition |
| `zod` | ^3.23.8 | Schema validation for all Server Actions and URL param parsing |
| `nodemailer` | ^7.0.11 | SMTP email sending — magic-link auth and contact form emails |
| `dompurify` | ^3.2.5 | XSS sanitization of contact form inputs |
| `bcrypt` | ^5.1.1 | Listed but not used in frontend source (likely a vestige of a removed credentials provider) |

### Dev Dependencies

| Package | Version | Role |
|---|---|---|
| `typescript` | ^5.4.5 | TypeScript compiler |
| `tailwindcss` | ^3.4.3 | CSS utility framework |
| `@tailwindcss/forms` | ^0.5.7 | Tailwind plugin for opinionated form element base styles |
| `postcss` | ^8 | CSS processing pipeline |
| `eslint` | ^8.57.0 | Linting |
| `eslint-config-next` | 16.0.10 | Next.js ESLint ruleset |
| `@typescript-eslint/*` | ^7.11.0 | TypeScript-specific ESLint rules (strict + stylistic profiles) |
| `@types/*` | Various | TypeScript type definitions |

---

## 13. TypeScript Types

All types are defined in `app/utils/definitions.ts`. ESLint enforces `type` over `interface` throughout the project.

```typescript
// Server action response envelope
type FormState = {
  errors?: Record<string, string[]>;
  message?: string | null;
  model_id?: string | null;
  timestamp?: string | null;
};

// Geocoding result from OpenStreetMap Nominatim
type CoordinateData = {
  lat: string;
  lon: string;
  display_name: string;
};

// Energy system model (input parameters + metadata)
type ModelData = {
  model_name: string;
  location: string;
  roof_incl: number;
  roof_azimuth: number;
  electr_cons: number;
  peak_power: number;
  battery_cap: number;
  sim_id?: string;          // set after a simulation is run
  model_id?: string;        // MongoDB ObjectId
  coordinates?: CoordinateData;
  time_created?: string;
};

// Simulation energy KPIs
type EnergyKPIs = {
  annual_consumption: number;
  pv_generation: number;
  grid_consumption: number;
  grid_feed_in: number;
  self_consumption: number;
  self_consumption_rate: number;
  self_sufficiency: number;
};

// Monthly PV generation data point
type PVMonthlyGen = {
  month: string;
  pv_generation: number;
};

// Simulation results envelope (from backend)
type SimResultsEval = {
  model_id: string;
  energy_kpis: EnergyKPIs;
  pv_monthly_gen: PVMonthlyGen[];
};

// Donut chart display data (derived from SimResultsEval)
type DonutChartData = {
  data: { name: string; value: number; share: number; tooltip: string }[];
  labels: { center: number; title: number };
  title: string;
};

// Power profile timeseries data point
type SimTimestep = {
  time: string;
  Load: number;
  PV: number;
  Battery: number;
  Total: number;
  StateOfCharge: number;
};

// Financial input parameters
type FinData = {
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

// Investment cost breakdown
type FinInvestment = {
  pv: number;
  battery: number;
  total: number;
};

// Financial KPIs (from backend)
type FinKPIs = {
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

// One year of financial projection data
type FinYearlyData = {
  year: number;
  cum_profit: number;
  cum_cash_flow: number;
  loan: number;
};

// Financial results envelope (from backend)
type FinResults = {
  model_id: string;
  fin_kpis: FinKPIs;
  yearly_data: FinYearlyData[];
};

// Financial line chart data point
type FinChartData = {
  "Year": number;
  "Cum. Profit"?: number;
  "Investment"?: number;
  "Cum. Cash Flow"?: number;
  "Loan"?: number;
};

// Financial bar chart item
type FinBarChartItem = {
  type: string;
  'PV'?: number;
  'Battery'?: number;
  'Cost savings'?: number;
  'Feed-in revenue'?: number;
  'Operation costs'?: number;
};

// Contact form fields
type EmailFormData = {
  name?: string;
  email?: string;
  category: string;
  message: string;
};
```

---

## 14. Configuration Files

### `next.config.mjs`
- Enables full URL logging for all server-side `fetch` calls (`logging: { fetches: { fullUrl: true } }`).
- Permits `next/image` to load remote images from `avatars.githubusercontent.com` (GitHub avatars) and `lh3.googleusercontent.com` (Google avatars).

### `tsconfig.json`
- Target: `esnext`, module: `esnext`, resolution: `bundler`
- `strict: true`
- Path alias: `@/*` → `./*` (root of `frontend/`)
- `jsx: preserve` (Next.js handles JSX transform)
- `incremental: true`

### `tailwind.config.ts`
- Dark mode: `class`-based
- Content paths include `./app/**` and the Tremor node_modules path
- Full Tremor design token configuration
- Large colour safelist for dynamically constructed Tremor class names
- Plugins: `@headlessui/tailwindcss`, `@tailwindcss/forms`

### `vercel.json`
- `{ "framework": "nextjs" }` — minimal Vercel deployment configuration

### `.eslintrc.json`
- Extends `next/core-web-vitals`, `@typescript-eslint/strict`, `@typescript-eslint/stylistic`
- Enforces `type` over `interface`: `@typescript-eslint/consistent-type-definitions: ["error", "type"]`

---

## 15. Environment Variables

No `.env` file is committed to the repository. In Docker Compose deployments, variables are supplied via `./frontend/.env`.

| Variable | Used In | Purpose |
|---|---|---|
| `MONGODB_URI` | `utils/db.ts` | MongoDB connection string for the NextAuth adapter |
| `BACKEND_BASE_URI` | `utils/helpers.ts` | Base URL of the FastAPI backend (e.g. `http://localhost:8000`) |
| `AUTH_SECRET` | NextAuth convention | Secret for signing JWT tokens |
| `AUTH_GITHUB_ID` | NextAuth convention | GitHub OAuth App Client ID |
| `AUTH_GITHUB_SECRET` | NextAuth convention | GitHub OAuth App Client Secret |
| `AUTH_GOOGLE_ID` | NextAuth convention | Google OAuth Client ID |
| `AUTH_GOOGLE_SECRET` | NextAuth convention | Google OAuth Client Secret |
| `EMAIL_HOST` | `auth.ts`, `helpers.ts` | SMTP server hostname |
| `EMAIL_PORT` | `auth.ts`, `helpers.ts` | SMTP server port |
| `EMAIL_SENDER` | `auth.ts`, `helpers.ts` | From-address for sent emails |
| `EMAIL_PASS` | `auth.ts`, `helpers.ts` | SMTP authentication password |
| `EMAIL_RECEIVER` | `helpers.ts` | Destination address for contact form submissions |
| `NODE_ENV` | `utils/db.ts` | Toggles MongoDB client caching strategy between dev and prod |

---

## 16. Key Architecture Decisions

These are the decisions with the most impact on the planned migration.

### All API calls are server-side only
The browser never directly contacts the FastAPI backend. Every fetch goes through a Next.js Server Component or Server Action. In the vanilla migration, a lightweight backend-for-frontend (BFF) layer — or direct fetch calls from the browser with a CORS-enabled backend — will need to replace this.

### Authentication is deeply integrated with the framework
NextAuth v5 provides OAuth and magic-link auth, session management, JWT signing, MongoDB persistence, and route-protection middleware. The vanilla replacement will need an explicit auth strategy: session cookies + a backend login endpoint, or an external auth service.

### No client-side data fetching library
There is no SWR or React Query. Caching is handled entirely by Next.js (`cache()`, `revalidatePath`). The vanilla app will need an explicit approach to data loading, error handling, and cache/refresh management.

### Tremor is the entire UI kit
Nearly all visual components — charts, inputs, buttons, cards, dialogs, dropdowns — come from `@tremor/react`. Replacing Tremor means either adopting a different component library or implementing these components from scratch in vanilla HTML/CSS/TS.

### Charts are Tremor-wrapped Recharts
Tremor's `DonutChart`, `BarChart`, and `LineChart` are built on top of Recharts. The vanilla migration will need a chart library (e.g. Chart.js, Apache ECharts, Recharts standalone) or a custom SVG/Canvas implementation.

### Model limit of 5 is enforced client-side
The "Create Model" button is disabled when `num_models >= 5`. This guard should also exist in the backend; the vanilla frontend will need to replicate this check.

### Progressive disclosure in the finance form
The advanced finance parameters are hidden by default. The vanilla implementation should replicate this UX, ensuring hidden fields still submit their values.

### URL search params as shareable chart state
The power chart date range is stored in the URL. This is a useful feature worth preserving in the vanilla implementation — it can be replicated with standard `URLSearchParams` and `history.replaceState`.
