# Ferntree Frontend Migration — Final Report

## Overview

This document is the design and architecture report for the migration of the Ferntree frontend from a Next.js 14 App Router application to a vanilla TypeScript single-page application (SPA). The migration was completed in full across nine phases. The resulting application is framework-free, statically deployable, and functionally equivalent to the pre-migration MVP.

---

## Pre-Migration Architecture (Next.js)

The original frontend was built with **Next.js 14 App Router**, **React 18**, **TypeScript**, and **Tailwind CSS**, with **Tremor** as the primary UI component library.

### Key characteristics

**Server-first rendering.** All data fetching happened server-side via async React Server Components and Next.js Server Actions. The browser never contacted the FastAPI backend directly. Next.js handled caching (`React.cache()`), cache invalidation (`revalidatePath()`), and request deduplication transparently.

**Authentication.** The app used Auth.js v5 (NextAuth beta) with three sign-in methods: GitHub OAuth, Google OAuth, and a Nodemailer magic-link email flow. Sessions were persisted to MongoDB via `@auth/mongodb-adapter`. Route protection was handled by a Next.js middleware running at the Edge.

**Component model.** The UI was composed of React Server Components (for data-fetching pages and layouts) and Client Components (for interactive elements such as forms, dropdowns, and charts). Shared UI came entirely from `@tremor/react`, which provided cards, dialogs, inputs, dropdowns, and chart wrappers built on top of Recharts.

**Routing.** Next.js App Router provided file-system routing with nested layouts, dynamic segments (`[model_id]`), and `<Suspense>`-bounded loading states. Navigation used `<Link>`, `redirect()`, and `router.push()` from `next/navigation`.

**Validation.** Zod validation ran exclusively server-side inside Server Actions. No client-side validation library was used.

### Dependency surface (selected)

| Concern | Library |
|---|---|
| Framework | `next@^14`, `react@^18` |
| Authentication | `next-auth@^5-beta`, `@auth/mongodb-adapter` |
| UI components | `@tremor/react@^3` |
| Charts | Tremor → Recharts |
| Styling | Tailwind CSS v3 |
| Validation | `zod@^3` (server-side) |
| Icons | `@remixicon/react` |
| Tooltips / Dropdowns | `@radix-ui/react-tooltip`, `@radix-ui/react-dropdown-menu` |

---

## Pre-Migration Simplification (MVP Baseline)

Before the migration began, the Next.js frontend was reduced to an MVP baseline in three rounds of changes:

1. **Auth strip.** All authentication infrastructure was removed — NextAuth, the login page, middleware, MongoDB client, contact form, and sign-out button. A fixed anonymous `user_id = 'mvp-user'` replaced the dynamic session-resolved user ID throughout all Server Actions.

2. **Complexity reduction.** UX polish features not required for core functionality were removed: skeleton/shimmer loading placeholders, `<Suspense>` fallbacks, chart category toggle dropdowns, the finance form's progressive disclosure (advanced field toggle), and Tremor `DateRangePicker` seasonal presets. These were replaced with simpler equivalents (plain date inputs, always-visible fields).

3. **Bug fixes.** A systematic code review identified and fixed 25 issues including missing `response.ok` guards, React key anti-patterns, unsafe type casts, incorrect number formatters, and an active nav highlight bug (`===` replaced with `startsWith`).

The MVP baseline served as the functional reference for the vanilla migration.

---

## Post-Migration Architecture (Vanilla TypeScript)

The vanilla app lives at `vanilla/` (sibling to `frontend/`) and is a framework-free SPA bundled by **Vite 5**.

### Target stack

| Concern | Technology |
|---|---|
| Language | TypeScript (ES2020 target) |
| Bundler | Vite 5 |
| Styling | Plain CSS with CSS custom properties |
| Charts | Chart.js 4 |
| Routing | Hand-rolled History API client-side router |
| HTTP | Browser `fetch` API |
| Forms + validation | Native HTML forms; Zod (client-side) |
| Icons | Inline SVG strings |
| Server runtime | None — static HTML/CSS/JS |

### Application shell

`index.html` is the single HTML file for all routes. It contains two top-level DOM elements that persist for the lifetime of the app:

- `<div id="app">` — the mount point. On boot, `main.ts` writes the persistent shell (sidenav + `<main id="content">`) into this element. Subsequent navigations replace only the `innerHTML` of `<main id="content">`.
- `<div id="loading-overlay">` — the full-screen loading overlay. Placed outside `#app` so it is never overwritten by navigation.

### Routing

`router.ts` implements a lightweight client-side router using the History API:

- A route table maps URL patterns (`:param` syntax compiled to regex) to `PageRenderer` functions.
- `navigate(path)` calls `history.pushState` and renders the matching page module into `<main id="content">`.
- A `popstate` listener handles browser Back/Forward.
- A same-URL guard prevents re-renders when navigating to the current path (required to avoid aborting in-progress async renders).
- Active nav highlighting uses `pathname.startsWith(link.dataset.href)` so sub-routes keep the parent link highlighted.

### Page modules

Each page is a TypeScript module that exports `render(container, params)`. The router calls this function on every navigation. The two detail routes (`/workspace/simulations/:model_id`, `/workspace/finances/:model_id`) share one module each with their index counterpart.

| Route | Module |
|---|---|
| `/workspace` | `pages/workspace.ts` |
| `/workspace/models` | `pages/models.ts` |
| `/workspace/simulations[/:model_id]` | `pages/simulations.ts` |
| `/workspace/finances[/:model_id]` | `pages/finances.ts` |

### Event listener lifecycle

`<main id="content">` is persistent and is never replaced between navigations. To prevent stale event listeners from accumulating across renders, each page module holds a module-level `AbortController` (`listenerController`). At the top of every `render()` call the controller is aborted and replaced. All `addEventListener` calls use `{ signal }` from this controller, so old listeners are automatically removed when a new render starts.

### API layer

`api.ts` contains one typed `async` function per backend endpoint. All functions call the FastAPI backend directly from the browser. The base URL is read from `import.meta.env.VITE_BACKEND_BASE_URI` (injected by Vite at build time). URLs are constructed by string concatenation (`BACKEND_BASE_URI + path`) — the two-argument `new URL(path, base)` constructor was avoided because it silently drops base path prefixes when `path` starts with `/`.

### Mock API

A Vite plugin (`mock-plugin.ts`) intercepts all requests to `/api/mock/*` and returns static JSON for all nine endpoints. This allows full end-to-end development without a running FastAPI or MongoDB instance. `.env.local` points `VITE_BACKEND_BASE_URI` at the local mock, so no external process is required.

### Charts

Chart.js 4 replaces Tremor/Recharts. Only the required components are imported and registered (tree-shaken). Key implementation notes:

- **Donut charts** use `Chart<'doughnut'>` as the explicit generic type parameter so TypeScript accepts the `cutout` option. Centre labels are drawn via a per-chart `afterDraw` plugin factory (`makeCentrePlugin(text)`) — plugins are not registered globally to prevent label bleed between canvases.
- **All chart instances** are stored in module-level variables and destroyed via `destroyCharts()` at the top of `render()`, preventing the "Canvas already in use" error on repeated navigation.
- **Line charts** use `animation: false`, `pointRadius: 0`, and `parsing: false` for performance with large timeseries datasets.
- **Chart containers** use `height` (not `max-height`) with `maintainAspectRatio: false` on the chart config so charts fill their containers correctly.

### Styling

The stylesheet (`src/styles/global.css`, ~1030 lines) uses CSS custom properties for all brand colours, spacing, radii, and shadow values. No CSS framework is used. Layouts use CSS Grid and Flexbox. The sidenav collapses to icon-only below 768px via a media query.

### Validation

Zod validation moved from server-side (inside Next.js Server Actions) to **client-side** (inside page modules). The same schemas and rules were ported verbatim. Form fields use `z.coerce.number()` to handle HTML's string-typed inputs automatically. Errors are displayed inline below each field via `<span class="form-error">` elements.

---

## Key Architecture Changes

| Concern | Next.js (before) | Vanilla TS (after) |
|---|---|---|
| Data fetching | Server Components / Server Actions (server-side only) | Browser `fetch` directly to FastAPI |
| Authentication | NextAuth v5 — OAuth + magic-link + JWT sessions | None — fixed `user_id = 'mvp-user'` |
| Routing | Next.js App Router (file-system) | Hand-rolled History API router |
| UI components | `@tremor/react` (Tailwind + Radix + Recharts) | Plain HTML/CSS |
| Charts | Tremor-wrapped Recharts | Chart.js 4 |
| Styling | Tailwind CSS v3 | Plain CSS custom properties |
| Forms | React `useFormState` / `useFormStatus` + Server Actions | Native HTML forms + client-side Zod |
| State | React component state + URL params | DOM + module-level variables + URL |
| Caching | `React.cache()`, `revalidatePath()` | Per-navigation `fetch()`, no cache layer |
| Server runtime | Node.js (Next.js server) | None — static files only |
| Bundle tooling | Next.js (webpack) | Vite 5 |
| Deployment target | Node.js host (Vercel / Docker) | Any static host (nginx, Caddy, CDN) |

---

## Dependencies Removed

The following production dependencies were eliminated entirely:

- `next`, `react`, `react-dom` — framework and component model
- `next-auth`, `@auth/mongodb-adapter`, `mongodb` — authentication and session persistence
- `@tremor/react`, `@headlessui/react`, `@headlessui/tailwindcss` — UI component library
- `@radix-ui/react-tooltip`, `@radix-ui/react-dropdown-menu`, `@radix-ui/react-checkbox` — UI primitives
- `@heroicons/react`, `@remixicon/react` — icon libraries
- `nodemailer` — email (magic-link auth and contact form)
- `dompurify` — XSS sanitization (contact form removed)
- `bcrypt` — unused vestige
- `clsx`, `tailwind-merge` — class merging utilities
- `tailwindcss`, `postcss`, `@tailwindcss/forms` — CSS framework

## Dependencies Added

| Package | Role |
|---|---|
| `chart.js@^4` | Charts (replaces Tremor/Recharts) |
| `zod@^3` | Client-side form validation (same library, moved to browser) |
| `vite@^5` | Bundler and dev server |
| `typescript@^5` | Compiler (same version) |

The final production bundle is **~285 KB JS / ~13 KB CSS** (Vite build output).

---

## Acceptance Testing

The migration was validated against a 329-item checklist covering all pages, components, interactions, and edge cases. Results:

- **326 items: PASS**
- **2 items: ACCEPTED AS-IS** — no-results states on the Simulations and Finances pages show a single card covering the full content area rather than one card per chart section (user-accepted deviation)
- **1 item: FIXED** — the Create Model form had `novalidate` set, suppressing native browser `required` validation; this was removed so browser validation runs before Zod

No console errors occur during normal user flows. Browser Back/Forward works correctly throughout all flows. Hard refreshes at any sub-route are handled correctly by Vite's built-in SPA history fallback.
