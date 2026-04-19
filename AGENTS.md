# AGENTS.md

## Repo layout

```
ferntree/
├── frontend/        # Vanilla TypeScript + Vite 5 SPA (NO React, NO Next.js)
├── backend/         # FastAPI (Python 3.12) + ferntree simulation engine
│   └── src/
│       ├── main.py              # all API routes
│       ├── sim/ferntree/        # custom PV simulation engine
│       ├── solar_data/          # PVGIS + Nominatim + GeoNames integrations
│       ├── utils/               # sim_funcs, auth_funcs
│       └── database/            # mongodb.py, models.py
├── Dockerfile                   # multi-stage: frontend-dev/prod + backend-dev/prod
└── compose.yml                  # dev stack (frontend + backend + mongodb)
```

No root-level `package.json` or `pyproject.toml`. Each service is self-contained.
`frontend_migration/` no longer exists — the migration to vanilla TS is complete.

## Running services

**Full dev stack (recommended):**
```bash
docker compose watch   # hot-reload via compose develop.watch
```

**Individually:**
```bash
# Backend (from repo root)
export PYTHONPATH=$(pwd)
uvicorn src.main:app --reload --app-dir backend

# Frontend (from frontend/)
npm run dev   # Vite dev server on port 5173
```

`PYTHONPATH` must be set to the repo root for `src.main` imports to resolve. `.vscode/settings.json` sets this automatically.

## Environment variables

- Backend reads `./backend/.env` (loaded via `python-dotenv`). Required: `MONGODB_URI`, `MONGODB_DATABASE`, `BACKEND_BASE_URI`, `FRONTEND_BASE_URI`.
- Frontend reads `./frontend/.env.local`. Key var: `VITE_BACKEND_BASE_URI`.
  - **Default in `.env.local` points to the mock plugin** (`http://localhost:5173/api/mock`), not the real FastAPI. To develop against the real backend, set `VITE_BACKEND_BASE_URI=http://localhost:8000`.
- Auth-related env vars (`AUTH_SECRET`, `AUTH_GITHUB_ID/SECRET`, etc.) are **no longer used** — authentication has been removed.

## Tests

**No automated tests exist** in either service. There is no `pytest.ini`, `conftest.py`, or `*.test.ts`.

## Linting and formatting

**Python — ruff (runs on pre-commit and should be run manually):**
```bash
ruff check --fix backend/
ruff format backend/
```
Config in `backend/pyproject.toml`. Rules: E, F, D (pydocstyle), I (isort). Target: Python 3.12. Notable ignores: `D100, D104, D203, D205, D213, D401`.

**TypeScript — no ESLint**. There is no `npm run lint` script and no `.eslintrc.json`. Run `npm run build` to typecheck:
```bash
# From frontend/
npm run build   # runs: tsc -p tsconfig.json && tsc -p tsconfig.node.json && vite build
```
Two tsconfigs: `tsconfig.json` (app, ES2020) and `tsconfig.node.json` (vite.config.ts + mock-plugin.ts, ES2022).

**Pre-commit runs ruff + file hygiene hooks on every commit.** Install once with `pre-commit install`. The devcontainer `postCreateCommand` does this automatically.

## Frontend architecture notes

The frontend was fully migrated from Next.js to **vanilla TypeScript + Vite**. Do not use any Next.js, React, or NextAuth patterns.

- **Entry point**: `frontend/index.html` → `frontend/src/main.ts`
- **Routing**: custom History API router in `frontend/src/router.ts`. Routes: `/workspace`, `/workspace/models`, `/workspace/simulations`, `/workspace/simulations/:model_id`, `/workspace/finances`, `/workspace/finances/:model_id`
- **Pages**: `frontend/src/pages/` — `workspace.ts`, `models.ts`, `simulations.ts`, `finances.ts`, `fin-results.ts`
- **API calls are browser-side**: `frontend/src/api.ts` makes `fetch()` calls directly to FastAPI from the client. There are no server components or server actions.
- **Authentication is gone**: no login, no sessions. All API calls pass a hardcoded `USER_ID = 'mvp-user'` query parameter (defined in `frontend/src/config.ts`).
- **No path alias**: `tsconfig.json` has no `paths` config — use relative imports.
- **Charting**: `chart.js@^4` directly (no Tremor, no Recharts).
- **Validation**: `zod@^3`.
- **No Tailwind, no Tremor, no Remixicon, no Heroicons**.
- **Mock plugin**: `frontend/mock-plugin.ts` is a Vite dev-server plugin intercepting `/api/mock/*` routes with static data. The default `.env.local` routes the app through this mock — no backend needed for frontend-only development.
- **Env vars**: use `import.meta.env.VITE_*` prefix (Vite convention), not `process.env` or `NEXT_PUBLIC_*`.
- **ESM-only**: `"type": "module"` in `package.json`.

## Backend architecture notes

- Entry point: `backend/src/main.py` (all FastAPI routes defined here).
- CORS is configured from the `FRONTEND_BASE_URI` env var (comma-split) plus `"*"` — effectively permissive in all environments.
- Async MongoDB via `motor`. No sync MongoDB driver dependency remains.
- `cvxpy` is commented out in `requirements.txt` — experimental battery optimisation, do not uncomment.
- The simulation engine lives in `backend/src/sim/ferntree/`. It runs a 1-year hourly PV+battery simulation, invoked by the `/workspace/simulations/run-sim` endpoint.

## CI / Docker

- CI (`.github/workflows/docker-ci.yml`) builds `ferntree-backend` and `ferntree-frontend` images on pushes to `main` or `develop` and on all PRs. Pushes to Docker Hub only on non-PR events.
- Builds for **both `linux/amd64` and `linux/arm64`** (multi-platform). Generates SBOM and provenance attestations.
- Docker build context is the **repo root** — Dockerfile copies `./frontend` and `./backend` from that root.
- Production Docker targets: `frontend-prod`, `backend-prod`.
- Note: `compose.yml` maps the frontend to port `3000:3000` but the Vite dev server listens on **5173** — this mapping is likely stale.
