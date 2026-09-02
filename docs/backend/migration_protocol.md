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
