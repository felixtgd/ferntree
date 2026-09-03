# Backend Database Migration Protocol

## Stage 1: Infra and Schema

**Status:** Implemented and verified.

### Scope

Stage 1 establishes the local PostgreSQL infrastructure and the idempotent target schema. It does not change the Python database clients or application data layer.

### Implemented Changes

#### `compose.yml`

- Replaced the `mongodb` service with `postgres:16`.
- Configured the local database:
  - User: `ferntree`
  - Password: `ferntree`
  - Database: `ferntree_db`
  - Host port: `5432`
- Added persistent `postgres_data` storage.
- Mounted `backend/schema.sql` at `/docker-entrypoint-initdb.d/schema.sql` so the schema is applied on first initialization of an empty volume.
- Added a `pg_isready` healthcheck.
- Updated `backend` to wait for a healthy `postgres` service.
- Replaced backend `MONGO_URI` with:

  ```text
  DATABASE_URL=postgresql://ferntree:ferntree@postgres:5432/ferntree_db
  ```

- Removed the unused frontend `MONGO_URI` environment entry.

#### `backend/schema.sql`

Added the idempotent PostgreSQL schema from the approved migration plan. It creates:

- `users`
- `models`
- `simulations`
- `sim_timesteps`
- `sim_results_eval`
- `pv_monthly_gen`
- `finances`
- `fin_results`
- `fin_yearly_data`
- `loadprofiles`

The schema includes foreign keys, cascading deletes, required indexes, and the single `mvp-user` seed record. Re-running the file is safe because tables and indexes use `IF NOT EXISTS`, and the user seed uses `ON CONFLICT (username) DO NOTHING`.

#### Environment files

- Added `backend/.env` with the local `DATABASE_URL`. This file is ignored by Git.
- Added committed template `backend/.env.example` with the same variable.

### Verification Performed

The schema was initialized and tested in an isolated `postgres:16` container.

- All 10 tables were created.
- The `users` table contained exactly the seeded `mvp-user` row with ID `1`.
- Reapplying `backend/schema.sql` completed without errors.
- `sim_timesteps` was confirmed to have the `idx_sim_timesteps_sim_time` index on `(sim_id, time)` and an `ON DELETE CASCADE` foreign key to `simulations(id)`.
- `git diff --check` completed without whitespace errors.

### Known Limitation

The backend is intentionally not runnable after Stage 1 alone. Existing Python code still imports MongoDB libraries and requires `MONGODB_URI` / `MONGODB_DATABASE`; those are replaced in Stages 2 and 3. PostgreSQL can be started independently with:

```bash
docker compose up -d postgres
```

Full `docker compose config` validation is currently blocked by an existing unrelated issue: `compose.yml` references `frontend/.env`, while the repository contains only `frontend/.env.local`.

### Follow-up Stages

- Stage 2: replace MongoDB dependencies with `psycopg` and `psycopg_pool`.
- Stage 3: implement the async PostgreSQL API data layer and FastAPI pool lifecycle.
- Stage 4: port the synchronous simulation engine database client.
- Stage 5: port load profile and cleanup scripts.

## Stage 4: Sim Engine Client

**Status:** Implemented.

### Scope

Stage 4 replaces the synchronous simulation-engine MongoDB client with a
psycopg 3 client. The simulation engine continues to run as a synchronous
subprocess and writes timestep rows directly to PostgreSQL.

### Implemented Changes

#### `backend/src/sim/ferntree/components/database/postgres.py`

- Added `PostgresClient`, using `DATABASE_URL` and a synchronous
  `psycopg.Connection`.
- Replaced the old MongoDB results document with deletion of existing
  `sim_timesteps` rows for the simulation ID, so reruns replace prior results.
- Added flat simulation configuration loading from `simulations`.
- Added load profile reads from the PostgreSQL array column.
- Added buffered timestep writes using PostgreSQL `COPY`, retaining the
  1000-row buffer.
- Flushes pending rows and closes the connection during shutdown.

#### Simulation callers

- Updated `sim_builder.py` and `sim_host.py` to use `PostgresClient`.
- `SimBuilder` regroups the flattened database settings into the nested
  device-specific dictionaries expected by the existing simulation devices.
- Existing device and controller classes remain unchanged.

### Verification Performed

- `python -m compileall -q backend/src/sim` completed successfully.
- `git diff --check` completed without whitespace errors.
- A direct client smoke test against the running PostgreSQL container verified
  flattened config loading, load profile array reads, and buffered `COPY`
  insertion of timestep data.
- Reinitializing the same client deleted the prior `sim_timesteps` rows,
  confirming rerun replacement semantics.

The full `docker compose` command remains blocked by the existing unrelated
missing `frontend/.env` file. The client verification used the healthy
PostgreSQL container directly and the built backend image.

### Follow-up Stages

- Stage 5: port load profile and cleanup scripts.
- Stage 6: run the complete flow and remove remaining MongoDB references.

## Stage 3: API Data Layer

**Status:** Implemented.

### Scope

Stage 3 replaces the asynchronous API data layer with psycopg 3 and wires the
PostgreSQL connection pool into the FastAPI application lifecycle. The
synchronous simulation-engine client and reference-data scripts remain for
Stages 4 and 5.

### Implemented Changes

#### `backend/src/database/postgres.py`

- Added a module-level `psycopg_pool.AsyncConnectionPool` using `DATABASE_URL`.
- Added the `Database` API client with typed model, simulation, evaluation,
  finance, and financial-result methods.
- Flattened nested coordinates and system settings on writes and reassembled
  the original Pydantic response shapes on reads.
- Resolved the external `user_id` username to the internal `users.id` foreign
  key while returning the username in API responses.
- Added string/integer ID conversion and not-found handling for malformed IDs.
- Added transactional parent upserts with child-row replacement for monthly
  PV generation and yearly financial data.
- Added `fetch_timesteps`, including model-to-simulation resolution and SQL
  time-range filtering against `sim_timesteps`.
- Added allowlisted `clean_collection` support for later cleanup-script use.

#### API callers

- Updated `main.py` to use typed PostgreSQL methods and the SQL-backed
  timeseries range query.
- Added FastAPI lifespan handling to open and close the async pool cleanly.
- Updated `auth_funcs.py` and `sim_funcs.py` to use the PostgreSQL client.
- Preserved string IDs and existing Pydantic/API response contracts.
- Model deletion now returns true only when a model row was deleted; foreign
  key cascades remove dependent rows.
- Model-scoped reads and writes are restricted to the requesting username,
  preventing cross-user access through sequential model IDs.
- CORS now uses only the configured frontend origins instead of combining a
  wildcard origin with credentialed requests.
- Timeseries queries apply the 480-row response cap in SQL, and finance form
  data for a user is loaded with one set-based query.

#### Verification support

- Added `backend/scripts/smoke_db.py`, which exercises model CRUD, simulation,
  evaluation, finance, and financial-result round trips, idempotent upserts,
  and model deletion cascade behavior.
- Added `backend/scripts/__init__.py` so the smoke script can run as a module.

### Verification Performed

- `python -m compileall -q backend/src` completed successfully.
- `python -m compileall -q backend/scripts backend/src` completed successfully.
- `git diff --check` completed without whitespace errors.

The repository does not have `ruff` installed in the current environment, so
the configured lint command could not be run. The database smoke script still
requires the PostgreSQL service and should be run with:

```bash
docker compose run --rm backend python -m scripts.smoke_db
```

### Known Limitation

Timeseries reads now target `sim_timesteps`, which is populated by the Stage 4
synchronous simulation-engine client. Full simulation and timeseries endpoint
verification remains deferred to Stage 6 as specified by the migration plan.

The API currently accepts `user_id` from the client without authenticating the
caller. Database ownership checks therefore protect data only when that value
is trusted; a caller who knows another username can impersonate that user.
Authentication from a verified session or token, with endpoint identity derived
from that credential, is required follow-up work.

### Follow-up Stages

- Stage 4: port the synchronous simulation-engine database client.
- Stage 5: port load profile and cleanup scripts.
- Stage 6: run the complete flow and remove remaining MongoDB code.

## Stage 2: Dependencies

**Status:** Implemented and verified.

### Scope

Stage 2 replaces MongoDB runtime dependencies with the PostgreSQL driver dependencies required by the API layer and simulation engine. It also changes the backend base image so the psycopg binary package can be installed from its glibc wheel.

### Implemented Changes

#### `backend/requirements.txt`

- Removed `certifi == 2024.7.4`, which was only used for MongoDB TLS CA configuration.
- Removed `motor >= 3.6.0`, which also removes its transitive `pymongo` and `bson` dependencies.
- Added pinned PostgreSQL dependencies:

  ```text
  psycopg[binary] == 3.3.5
  psycopg-pool == 3.3.1
  ```

#### `Dockerfile`

- Changed the `backend-base` image from `python:3.12-alpine` to `python:3.12-slim`.
- `psycopg[binary]` provides glibc-compatible wheels but no musl-compatible Alpine wheel, so the Debian slim base is required for a reliable binary installation.
- Replaced the commented Alpine-specific cvxpy build-dependency command with its Debian `apt-get` equivalent.

### Verification Performed

- `docker compose build backend` completed successfully.
- The built image imports `psycopg` and `psycopg_pool`; `psycopg.__version__` is `3.3.5`.
- `motor` raises the expected `ModuleNotFoundError`.
- `pymongo` raises the expected `ModuleNotFoundError`.
- `git diff --check` completed without whitespace errors.

The Mongo absence checks were run directly against `ferntree-backend` with `docker run`. Parallel `docker compose run` commands conflicted while each attempted to create the existing `ferntree-postgres-1` dependency; no database service is required for import verification.

### Known Limitation

The backend remains intentionally non-runnable after this stage. Existing MongoDB client modules and load profile scripts still import removed MongoDB packages. Stages 3, 4, and 5 replace those imports with psycopg-based implementations.

### Follow-up Stages

- Stage 3: implement the async PostgreSQL API data layer and FastAPI pool lifecycle.
- Stage 4: port the synchronous simulation engine database client.
- Stage 5: port load profile and cleanup scripts.
