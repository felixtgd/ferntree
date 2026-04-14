# AGENTS.md

## Repo layout

```
ferntree/
├── frontend/        # Next.js 14 App Router (TypeScript + Tailwind + Tremor)
├── backend/         # FastAPI (Python 3.12) + ferntree simulation engine
│   └── src/
│       ├── main.py              # all API routes
│       ├── sim/ferntree/        # custom PV simulation engine
│       ├── solar_data/          # PVGIS + Nominatim + GeoNames integrations
│       ├── utils/               # sim_funcs, auth_funcs
│       └── database/            # mongodb.py, models.py
├── Dockerfile                   # multi-stage: frontend-dev/prod + backend-dev/prod
├── compose.yml                  # dev stack (frontend + backend + mongodb)
└── frontend_migration/          # architecture docs for planned vanilla TS migration
```

No root-level `package.json` or `pyproject.toml`. Each service is self-contained.

## Running services

**Full dev stack (recommended):**
```bash
docker compose watch   # hot-reload via compose develop.watch
```

**Individually:**
```bash
# Backend (from repo root)
uvicorn src.main:app --reload   # PYTHONPATH must include repo root

# Frontend (from frontend/)
npm run dev
```

`PYTHONPATH` must be set to the repo root for backend imports to resolve. `.vscode/settings.json` sets this automatically; elsewhere do `export PYTHONPATH=$(pwd)`.

## Environment variables

Backend reads `./backend/.env`, frontend reads `./frontend/.env`. Neither file is committed.

Required variables (see root `README.md` for full list):
- `MONGODB_URI`, `MONGODB_DATABASE`
- `BACKEND_BASE_URI`, `FRONTEND_BASE_URI`
- `AUTH_SECRET`, `AUTH_GITHUB_ID/SECRET`, `AUTH_GOOGLE_ID/SECRET`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_SENDER`, `EMAIL_PASS`, `EMAIL_RECEIVER`

## Tests

**No automated tests exist** in either service. There is no `pytest.ini`, `conftest.py`, or `*.test.ts`.

## Linting and formatting

**Python — ruff (auto-fix on save and pre-commit):**
```bash
ruff check --fix backend/
ruff format backend/
```
Config in `backend/pyproject.toml`. Rules: E, F, D (pydocstyle), I (isort). Target: Python 3.12.

**TypeScript — ESLint (Next.js strict profile):**
```bash
cd frontend && npm run lint
```
Config in `frontend/.eslintrc.json`. Enforces `type` over `interface` — do not use `interface` for type definitions.

**Pre-commit runs ruff + file hygiene hooks on every commit.** Install once with `pre-commit install`. The devcontainer `postCreateCommand` does this automatically.

## Frontend architecture notes

- **App Router only** (`app/` directory). No Pages Router, no `getServerSideProps`/`getStaticProps`.
- **All backend API calls are server-side** — inside Server Components or Server Actions marked `'use server'`. The browser never fetches the FastAPI backend directly.
- **Authentication** uses NextAuth v5 beta (`next-auth@^5.0.0-beta.30`). Config is split: `auth.config.ts` is edge-safe (used by `middleware.ts`); `auth.ts` adds the MongoDB adapter + Nodemailer and must run on Node.js only.
- **Primary UI library is Tremor** (`@tremor/react`). Charts (DonutChart, BarChart, LineChart) are Tremor wrappers around Recharts. Radix UI provides Tooltip and DropdownMenu primitives not covered by Tremor.
- **Icon library is `@remixicon/react`** — used almost exclusively. `@heroicons/react` is installed but barely used.
- **Path alias `@/*`** maps to `frontend/` root in `tsconfig.json`.
- **`bcrypt`** is listed in `package.json` but unused in source (vestige of a removed credentials provider).
- The Tailwind config has a large `safelist` for all colour scale classes — required for Tremor's dynamic class names. Do not remove it.
- `frontend_migration/nextjs_architecture.md` contains a full page/component/API inventory useful for understanding the frontend before making large changes.

## Backend architecture notes

- Entry point: `backend/src/main.py` (all FastAPI routes defined here).
- Async MongoDB via `motor`. The sync `mongodb` driver is only used in the frontend's NextAuth adapter.
- `cvxpy` is commented out in `requirements.txt` — experimental battery optimisation, do not uncomment.
- The simulation engine lives in `backend/src/sim/ferntree/`. It runs a 1-year hourly PV+battery simulation and is invoked by the `/workspace/simulations/run-sim` endpoint.

## CI / Docker

- CI (`.github/workflows/docker-ci.yml`) builds and pushes `ferntree-backend` and `ferntree-frontend` images to Docker Hub on pushes to `main` or `develop`.
- Docker build context is the **repo root**, not the service subdirectory. The Dockerfile copies `./frontend` and `./backend` from that root.
- Production Docker targets: `frontend-prod`, `backend-prod`.
