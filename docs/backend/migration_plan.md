# Backend Database Migration: MongoDB → PostgreSQL

> **Status:** Approved plan, not yet implemented.
> **Audience:** Engineers/agents implementing the migration in separate working sessions.
> **Scope:** Backend only (`backend/`). The frontend talks to Mongo **only** via the backend API, so no frontend DB code changes are required (one config value is discussed in Stage 3).

This document is intended to be self-contained. It captures every decision, the full target SQL schema, field-by-field mappings, and per-stage work packages (steps, success criteria, verification). Each stage is an independently implementable and verifiable work package.

---

## 1. Background & current state

The backend is **Python 3.12 / FastAPI** (async). It currently uses **two** MongoDB clients:

| Client | File | Driver | Runtime |
|---|---|---|---|
| API data layer | `backend/src/database/mongodb.py` | Motor (async) | FastAPI event loop |
| Sim engine | `backend/src/sim/ferntree/components/database/mongodb.py` | PyMongo (sync) | standalone subprocess (no event loop) |

The FastAPI app is **async top to bottom**: endpoints in `backend/src/main.py` await async helpers in `backend/src/utils/sim_funcs.py`, which await external I/O (PVGIS API, geolocation) and DB calls. The simulation engine runs as a **synchronous subprocess**, launched via `subprocess.run(["python", "src/sim/ferntree/ferntree.py", "--sim_id", <id>, "--model_id", <id>])` (`backend/src/utils/sim_funcs.py:155-165`). The subprocess inherits the parent process environment, so a single `DATABASE_URL` env var propagates to it.

### Current MongoDB collections
`users`, `models`, `simulations`, `sim_results_ts`, `sim_results_eval`, `finances`, `fin_results`, `loadprofiles`.

Pydantic models (kept as-is; they remain the API request/response contracts):
- API models: `backend/src/database/models.py`
- Sim engine models: `backend/src/sim/ferntree/components/database/models.py`

---

## 2. Confirmed decisions

1. **Greenfield** — no data ETL/backfill. Only reference data (`loadprofiles`) must be re-seeded.
2. **Driver:** a single dependency `psycopg` (psycopg 3), used **async in the API layer** (`psycopg.AsyncConnection` + `psycopg_pool.AsyncConnectionPool`) and **sync in the sim engine** (`psycopg.Connection`). Rationale: the API is already async (smallest diff from Motor, no thread-pool wrappers); the sim engine has no event loop so sync is the natural fit; psycopg 3 covers both from one package.
3. **Schema:** fully normalized relational tables. Strict 1:1 nested objects are flattened into their parent table; true 1:N arrays become child tables. Large numeric arrays that are always read/written whole (`T_amb`, `G_i`, `load_profile`) are stored as `DOUBLE PRECISION[]` columns (a pragmatic exception to full normalization).
4. **Primary keys:** `BIGSERIAL` integers. IDs are serialized as **strings** at the API boundary to preserve the existing frontend contract (the frontend treats model/sim IDs as opaque strings).
5. **Users descoped:** seed a single dummy user with `username = 'mvp-user'`. The frontend already sends a hardcoded `user_id=mvp-user` (`frontend/src/config.ts:5`, `frontend/src/api.ts:20`). Backend resolves the incoming `user_id` string to that user's internal integer id via a `username` column. No user-creation endpoint is added.
6. **Sim re-run semantics:** re-running a simulation for a model **replaces** prior results. The `simulations` row is stable per model (upsert by `model_id`, `RETURNING id`), giving a stable `sim_id`; the sim engine deletes existing `sim_timesteps` for that `sim_id` before writing fresh rows. (This fixes a latent Mongo bug — see §7.)
7. **Datetimes:** `time_created` and `run_time` (currently ISO strings) → `TIMESTAMPTZ`. The per-timestep `time` (epoch float) stays `DOUBLE PRECISION`.
8. **Money/float fields:** keep `DOUBLE PRECISION` (parity with current Python floats).
9. **Hosting:** local/compose Postgres only for now; `DATABASE_URL` allows adding `sslmode` later for a managed host.
10. **Migrations tooling:** none. A single idempotent `backend/schema.sql` is the source of truth (future schema changes are manual). Applied via the Postgres container's `/docker-entrypoint-initdb.d/`.

---

## 3. Target SQL schema

Place this in **`backend/schema.sql`**. It is idempotent (`CREATE TABLE IF NOT EXISTS`, `ON CONFLICT` seed). Table creation order avoids forward references; `models.sim_id` is a plain `BIGINT` (no FK) to avoid a circular dependency with `simulations`.

```sql
-- backend/schema.sql
-- PostgreSQL schema for the Ferntree backend (migrated from MongoDB).
-- Idempotent: safe to run multiple times.

-- =========================================================================
-- users  (auth descoped; single seeded dummy user)
-- =========================================================================
CREATE TABLE IF NOT EXISTS users (
    id             BIGSERIAL PRIMARY KEY,
    username       TEXT NOT NULL UNIQUE,     -- external identifier, e.g. 'mvp-user'
    name           TEXT,
    email          TEXT,
    image          TEXT,
    email_verified TIMESTAMPTZ
);

-- =========================================================================
-- models
-- =========================================================================
CREATE TABLE IF NOT EXISTS models (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_name          TEXT NOT NULL,
    location            TEXT NOT NULL,
    roof_incl           INTEGER NOT NULL,
    roof_azimuth        INTEGER NOT NULL,
    electr_cons         DOUBLE PRECISION NOT NULL,
    peak_power          DOUBLE PRECISION NOT NULL,
    battery_cap         DOUBLE PRECISION NOT NULL,
    time_created        TIMESTAMPTZ,
    sim_id              BIGINT,              -- mirror of simulations.id; no FK (avoids cycle)
    -- optional coordinates (Coordinates sub-doc, flattened)
    coord_lat           TEXT,
    coord_lon           TEXT,
    coord_display_name  TEXT
);
CREATE INDEX IF NOT EXISTS idx_models_user_id ON models(user_id);

-- =========================================================================
-- simulations  (1:1 with models; SystemSettings flattened)
-- =========================================================================
CREATE TABLE IF NOT EXISTS simulations (
    id                          BIGSERIAL PRIMARY KEY,
    model_id                    BIGINT NOT NULL UNIQUE REFERENCES models(id) ON DELETE CASCADE,
    run_time                    TIMESTAMPTZ,
    timezone                    TEXT,
    timebase                    INTEGER,
    planning_horizon            INTEGER,
    -- weather/irradiance input arrays (always read/written whole)
    t_amb                       DOUBLE PRECISION[],
    g_i                         DOUBLE PRECISION[],
    -- coordinates (dict[str,str] in SimDataIn, flattened)
    coord_lat                   TEXT,
    coord_lon                   TEXT,
    coord_display_name          TEXT,
    -- system_settings.baseload
    baseload_annual_consumption DOUBLE PRECISION,
    baseload_profile_id         INTEGER,
    -- system_settings.pv
    pv_roof_tilt                INTEGER,
    pv_roof_azimuth             INTEGER,
    pv_peak_power               DOUBLE PRECISION,
    -- system_settings.battery
    battery_capacity            DOUBLE PRECISION,
    battery_max_power           DOUBLE PRECISION,
    battery_soc_init            DOUBLE PRECISION,
    -- system_settings.battery.battery_ctrl
    batctrl_planning_horizon    INTEGER,
    batctrl_useable_capacity    DOUBLE PRECISION,
    batctrl_greedy              BOOLEAN,
    batctrl_opt_fill            BOOLEAN
);

-- =========================================================================
-- sim_timesteps  (was sim_results_ts.timeseries; 1 row per timestep)
-- =========================================================================
CREATE TABLE IF NOT EXISTS sim_timesteps (
    id           BIGSERIAL PRIMARY KEY,
    sim_id       BIGINT NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    time         DOUBLE PRECISION NOT NULL,   -- epoch seconds
    t_amb        DOUBLE PRECISION,
    p_solar      DOUBLE PRECISION,
    p_base       DOUBLE PRECISION,
    p_pv         DOUBLE PRECISION,
    p_bat        DOUBLE PRECISION,
    soc_bat      DOUBLE PRECISION,
    fill_level   DOUBLE PRECISION,
    p_load_pred  DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_sim_timesteps_sim_time ON sim_timesteps(sim_id, time);

-- =========================================================================
-- sim_results_eval  (1:1 with models; EnergyKPIs flattened)
-- =========================================================================
CREATE TABLE IF NOT EXISTS sim_results_eval (
    id                    BIGSERIAL PRIMARY KEY,
    model_id              BIGINT NOT NULL UNIQUE REFERENCES models(id) ON DELETE CASCADE,
    annual_consumption    DOUBLE PRECISION,
    pv_generation         DOUBLE PRECISION,
    grid_consumption      DOUBLE PRECISION,
    grid_feed_in          DOUBLE PRECISION,
    self_consumption      DOUBLE PRECISION,
    self_consumption_rate DOUBLE PRECISION,
    self_sufficiency      DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS pv_monthly_gen (
    id            BIGSERIAL PRIMARY KEY,
    eval_id       BIGINT NOT NULL REFERENCES sim_results_eval(id) ON DELETE CASCADE,
    month         TEXT NOT NULL,
    pv_generation DOUBLE PRECISION NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pv_monthly_gen_eval ON pv_monthly_gen(eval_id);

-- =========================================================================
-- finances  (1:1 with models; FinFormData)
-- =========================================================================
CREATE TABLE IF NOT EXISTS finances (
    id             BIGSERIAL PRIMARY KEY,
    model_id       BIGINT NOT NULL UNIQUE REFERENCES models(id) ON DELETE CASCADE,
    electr_price   DOUBLE PRECISION,
    feed_in_tariff DOUBLE PRECISION,
    pv_price       DOUBLE PRECISION,
    battery_price  DOUBLE PRECISION,
    useful_life    INTEGER,
    module_deg     DOUBLE PRECISION,
    inflation      DOUBLE PRECISION,
    op_cost        DOUBLE PRECISION,
    down_payment   DOUBLE PRECISION,
    pay_off_rate   DOUBLE PRECISION,
    interest_rate  DOUBLE PRECISION
);

-- =========================================================================
-- fin_results  (1:1 with models; FinKPIs + FinInvestment flattened)
-- =========================================================================
CREATE TABLE IF NOT EXISTS fin_results (
    id                   BIGSERIAL PRIMARY KEY,
    model_id             BIGINT NOT NULL UNIQUE REFERENCES models(id) ON DELETE CASCADE,
    -- fin_kpis.investment
    investment_pv        DOUBLE PRECISION,
    investment_battery   DOUBLE PRECISION,
    investment_total     DOUBLE PRECISION,
    -- fin_kpis scalars
    break_even_year      DOUBLE PRECISION,
    cum_profit           DOUBLE PRECISION,
    cum_cost_savings     DOUBLE PRECISION,
    cum_feed_in_revenue  DOUBLE PRECISION,
    cum_operation_costs  DOUBLE PRECISION,
    lcoe                 DOUBLE PRECISION,
    solar_interest_rate  DOUBLE PRECISION,
    loan                 DOUBLE PRECISION,
    loan_paid_off        DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fin_yearly_data (
    id             BIGSERIAL PRIMARY KEY,
    fin_results_id BIGINT NOT NULL REFERENCES fin_results(id) ON DELETE CASCADE,
    year           INTEGER NOT NULL,
    cum_profit     DOUBLE PRECISION,
    cum_cash_flow  DOUBLE PRECISION,
    loan           DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_fin_yearly_data_parent ON fin_yearly_data(fin_results_id);

-- =========================================================================
-- loadprofiles  (reference data; load_profile array read whole)
-- =========================================================================
CREATE TABLE IF NOT EXISTS loadprofiles (
    id           BIGSERIAL PRIMARY KEY,
    profile_id   INTEGER NOT NULL UNIQUE,
    type         TEXT,
    load_profile DOUBLE PRECISION[] NOT NULL
);

-- =========================================================================
-- Seed the dummy user (auth descoped)
-- =========================================================================
INSERT INTO users (username, name, email, image, email_verified)
VALUES ('mvp-user', 'MVP User', 'mvp@example.com', '', NULL)
ON CONFLICT (username) DO NOTHING;
```

---

## 4. Field mappings (Mongo/Pydantic → Postgres)

IDs: Mongo `ObjectId` (string) → Postgres `BIGSERIAL` (integer). At the API boundary, convert **int → str** on the way out and **str → int** on the way in. Guard non-integer IDs (return not-found, do not crash).

| Pydantic model (`backend/src/database/models.py`) | Postgres table | Notes |
|---|---|---|
| `User` | `users` | `emailVerified` → `email_verified`. `user_id` is external → `username`. |
| `ModelDataIn` / `ModelDataOut` | `models` | `_id` → `id`; `Coordinates` sub-doc → `coord_lat/coord_lon/coord_display_name`; `sim_id` mirror kept. `model_id` (out) = `str(id)`. |
| `SimDataIn` / `SimDataOut` | `simulations` | `T_amb`/`G_i` → `t_amb[]`/`g_i[]`; `coordinates` dict → `coord_*`; `SystemSettings` flattened (see below). `sim_id` = `str(id)`. |
| `SystemSettings.baseload` (`Baseload`) | `simulations.baseload_*` | `annual_consumption`, `profile_id`. |
| `SystemSettings.pv` (`PV`) | `simulations.pv_*` | `roof_tilt`, `roof_azimuth`, `peak_power`. |
| `SystemSettings.battery` (`Battery`) | `simulations.battery_*` | `capacity`, `max_power`, `soc_init`. |
| `Battery.battery_ctrl` (`BatteryCtrl`) | `simulations.batctrl_*` | `planning_horizon`, `useable_capacity`, `greedy`, `opt_fill`. |
| `SimTimestep` / sim-engine `TimestepData` | `sim_timesteps` | one row per element of the old `timeseries` array. |
| `SimResultsEval` + `EnergyKPIs` | `sim_results_eval` | KPI fields flattened; keyed by `model_id`. |
| `PVMonthlyGen` | `pv_monthly_gen` | child of `sim_results_eval` (FK `eval_id`). |
| `FinFormData` | `finances` | flat; keyed by `model_id`. |
| `FinResults` + `FinKPIs` + `FinInvestment` | `fin_results` | investment flattened to `investment_*`; keyed by `model_id`. |
| `FinYearlyData` | `fin_yearly_data` | child of `fin_results` (FK `fin_results_id`). |
| sim-engine `LoadProfile` | `loadprofiles` | `load_profile` → `DOUBLE PRECISION[]`. |

**Reassembly guidance (for typed fetches):** when reading back, rebuild the nested Pydantic shape from the flat columns / child rows. Example — `SimResultsEval` = row from `sim_results_eval` (→ `EnergyKPIs`) + all `pv_monthly_gen` rows for that `eval_id` (→ `list[PVMonthlyGen]`). Example — `FinResults` = row from `fin_results` (→ `FinKPIs` incl. `FinInvestment`) + `fin_yearly_data` rows (→ `list[FinYearlyData]`).

---

## 5. Configuration & connection details

### Environment variables
Replace `MONGODB_URI` + `MONGODB_DATABASE` (and the mismatched `MONGO_URI` in `compose.yml`) with a single:

```
DATABASE_URL=postgresql://ferntree:ferntree@postgres:5432/ferntree_db
```

- Read in the API client, the sim-engine client, and the loadprofile ETL scripts.
- The sim-engine subprocess inherits this from the parent env; keep its `load_dotenv` fallback working by ensuring the same var name.
- For a future managed host, append `?sslmode=require`.

Update/add `backend/.env` and create `backend/.env.example`. (No `.env` files are committed today.)

### psycopg usage patterns (reference snippets)

**Async pool (API layer)** — open on startup, close on shutdown:
```python
from psycopg_pool import AsyncConnectionPool

pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False)
# on FastAPI startup:  await pool.open()
# on FastAPI shutdown: await pool.close()

async with pool.connection() as conn:
    async with conn.cursor() as cur:
        await cur.execute("SELECT id FROM users WHERE username = %s", (user_id,))
        row = await cur.fetchone()
```

**Upsert returning id (both insert and update):**
```sql
INSERT INTO simulations (model_id, run_time, ...) VALUES (%s, %s, ...)
ON CONFLICT (model_id) DO UPDATE SET run_time = EXCLUDED.run_time, ...
RETURNING id;
```

**Sync connection + bulk COPY (sim engine timesteps):**
```python
import psycopg

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM sim_timesteps WHERE sim_id = %s", (sim_id,))
        cols = ("sim_id","time","t_amb","p_solar","p_base","p_pv","p_bat",
                "soc_bat","fill_level","p_load_pred")
        with cur.copy(f"COPY sim_timesteps ({','.join(cols)}) FROM STDIN") as copy:
            for r in batch:
                copy.write_row((sim_id, r["time"], r["T_amb"], r["P_solar"],
                                r["P_base"], r["P_pv"], r["P_bat"], r["Soc_bat"],
                                r["fill_level"], r["P_load_pred"]))
    conn.commit()
```

### compose.yml — replacement Postgres service (reference)
```yaml
  postgres:
    image: postgres:16
    environment:
      - POSTGRES_USER=ferntree
      - POSTGRES_PASSWORD=ferntree
      - POSTGRES_DB=ferntree_db
    ports:
      - 5432:5432
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/schema.sql:/docker-entrypoint-initdb.d/schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ferntree -d ferntree_db"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```
Update `backend`: `depends_on: postgres` with `condition: service_healthy`, set `DATABASE_URL`. Remove the `MONGO_URI` env from both `frontend` and `backend`.

> Note: `/docker-entrypoint-initdb.d/` runs **only on an empty data volume**. To re-apply the schema during development, either `docker compose down -v` (wipes the volume) or apply `schema.sql` manually with `psql` (it is idempotent).

### requirements.txt changes
- **Remove:** `motor >= 3.6.0`; `certifi == 2024.7.4` (Mongo TLS CA no longer needed).
- **Remove transitive Mongo:** `pymongo`/`bson` came via Motor; ensure no direct pin remains.
- **Add:** `psycopg[binary]`, `psycopg_pool`.

---

## 6. Files to change (inventory)

| File | Action |
|---|---|
| `backend/schema.sql` | **New.** DDL from §3. |
| `compose.yml` | Replace `mongodb` service with `postgres`; fix env vars; update `depends_on`. |
| `backend/.env`, `backend/.env.example` | Replace Mongo vars with `DATABASE_URL`. |
| `backend/requirements.txt` | Swap Mongo libs for psycopg (see §5). |
| `backend/src/database/mongodb.py` | Replace with `backend/src/database/postgres.py` (async psycopg). Keep method surface. |
| `backend/src/database/models.py` | Keep Pydantic models; drop any `bson` usage. |
| `backend/src/main.py` | Update import of the DB client; move timeseries date filter into SQL (`main.py:305-318`); wire pool open/close into app lifespan. |
| `backend/src/utils/auth_funcs.py` | Update import/type of DB client (`auth_funcs.py:6`). |
| `backend/src/utils/sim_funcs.py` | Update DB client import/type references (`mongodb.MongoClient`). |
| `backend/src/sim/ferntree/components/database/mongodb.py` | Rewrite as sync psycopg client (keep class/method names used by callers). |
| `backend/src/sim/ferntree/components/database/models.py` | No change (Pydantic). |
| `backend/src/sim/ferntree/sim_builder.py`, `.../components/host/sim_host.py` | Verify they still call the (renamed) client correctly. |
| `backend/src/sim/loadprofiles/alpg_profiles.py`, `pipeline_gold.py` | Port inserts to Postgres `loadprofiles`. |
| `backend/src/clean_database.py` | Port to `TRUNCATE ... RESTART IDENTITY CASCADE`. |

### Current API DB method surface to preserve (`backend/src/database/mongodb.py`)
`check_user_exists`, `insert_model`, `fetch_models`, `update_sim_id_of_model`, `delete_model`, `fetch_model_by_id`, `fetch_document`, `insert_document`, `clean_collection`.
Callers: `main.py` (`:84,115,144,180,186,193,233,249,289,301,354,368,371,408,441,447`), `auth_funcs.py:57`, `sim_funcs.py:196,358,361`, `clean_database.py`.

> `fetch_document(collection, model_id)` and `insert_document(collection, document)` are generic in Mongo. In Postgres, replace them with **typed** per-table fetch/upsert helpers that reassemble the exact nested Pydantic shapes. Preserve the external behavior (same inputs/outputs) so callers change minimally.

### Sim-engine client method surface (`.../components/database/mongodb.py`)
`__init__(sim_id, model_id)`, `load_config()`, `get_load_profile(profile_id)`, `write_timeseries_data_to_db(results)`, `write_batch(batch)`, `shutdown()`. Callers: `sim_builder.py:34,60`, `sim_host.py:68,116`.

---

## 7. Important behavioral note (latent Mongo bug fixed by migration)

In `run_simulation` (`backend/src/main.py:186`), `sim_id = insert_document("simulations", ...)` returns `result.upserted_id` from a Mongo `replace_one(upsert=True)` (`mongodb.py:227-236`). Mongo only populates `upserted_id` on **insert**, not update — so re-running a simulation for an existing model yields `sim_id = "None"` and breaks downstream. The Postgres `INSERT ... ON CONFLICT (model_id) DO UPDATE ... RETURNING id` returns the id in **both** cases, making `sim_id` stable per model. The sim engine must therefore `DELETE FROM sim_timesteps WHERE sim_id = %s` before writing new results (replacing the Mongo `replace_one` that reset the `timeseries` array). This yields the confirmed "re-run replaces prior results" behavior.

---

## 8. Stages (work packages)

Stages 1 and 2 are prerequisites for 3/4/5. Each of Stages 3, 4, 5 is verifiable on its own (using API calls, a direct smoke script, or SQL fixtures) — no stage requires a *later* stage to prove itself. Stage 6 is the integration gate. Work on a branch; Mongo code remains intact until Stage 6, so any stage can be reverted independently.

Connection info for verification commands below assumes the compose service `postgres` with user/db `ferntree`/`ferntree_db`. Adjust as needed.

---

### Stage 1 — Infra & schema

**Prerequisites:** none.

**Steps**
1. Replace the `mongodb` service in `compose.yml` with the `postgres` service (see §5 reference block). Add the `postgres_data` volume.
2. Update `backend`: `depends_on: postgres` with `condition: service_healthy`; add `DATABASE_URL`. Remove `MONGO_URI` from `frontend` and `backend`.
3. Author `backend/schema.sql` exactly as in §3.
4. Update `backend/.env` and add `backend/.env.example` with `DATABASE_URL` (remove `MONGODB_URI`/`MONGODB_DATABASE`).

**Success criteria**
- `docker compose up` brings Postgres to healthy; backend waits for it.
- All tables + child tables exist; the `mvp-user` row is present.
- `schema.sql` is idempotent (re-applying causes no errors).

**Verification**
```bash
docker compose up -d postgres
docker compose exec postgres psql -U ferntree -d ferntree_db -c "\dt"        # lists all tables
docker compose exec postgres psql -U ferntree -d ferntree_db -c "SELECT id, username FROM users;"  # one mvp-user row
# idempotency:
docker compose exec -T postgres psql -U ferntree -d ferntree_db < backend/schema.sql   # no errors
docker compose exec postgres psql -U ferntree -d ferntree_db -c "\d+ sim_timesteps"    # (sim_id,time) index + cascade FK
```

---

### Stage 2 — Dependencies

**Prerequisites:** none (can run parallel to Stage 1).

**Steps**
1. `backend/requirements.txt`: remove `motor`, `certifi`; ensure no direct `pymongo`/`bson`; add `psycopg[binary]`, `psycopg_pool`.
2. Rebuild the backend image.

**Success criteria**
- Image builds; `psycopg` + `psycopg_pool` import; Mongo libs gone.

**Verification**
```bash
docker compose build backend
docker compose run --rm backend python -c "import psycopg, psycopg_pool; print(psycopg.__version__)"  # v3.x
docker compose run --rm backend python -c "import motor"   # expect ModuleNotFoundError
```

---

### Stage 3 — API data layer (async psycopg)

**Prerequisites:** Stages 1–2.

**Steps**
1. Create `backend/src/database/postgres.py` with a `Database` class holding a module-level `AsyncConnectionPool`. Wire `pool.open()`/`pool.close()` into the FastAPI lifespan in `backend/src/main.py`.
2. Implement the preserved method surface (§6):
   - `check_user_exists(user_id)` — resolve `username`→id; return bool.
   - `insert_model(model)` — resolve `username`→internal id for FK; `INSERT ... RETURNING id`; flatten optional coordinates; return `str(id)`.
   - `fetch_models(user_id)` / `fetch_model_by_id(id)` — reassemble `ModelDataOut` (int id → str).
   - `update_sim_id_of_model(model_id, sim_id)`.
   - `delete_model(model_id)` — single `DELETE FROM models WHERE id=%s` (FK cascade replaces the manual multi-collection loop).
   - Typed replacements for `fetch_document`/`insert_document` covering `simulations`, `sim_results_eval`, `finances`, `fin_results`: upsert with `ON CONFLICT (model_id) DO UPDATE ... RETURNING id`; for `sim_results_eval` and `fin_results`, do parent upsert + child delete/re-insert in **one transaction**.
   - `clean_collection`/equivalent — `TRUNCATE ... RESTART IDENTITY CASCADE`.
3. Add int↔str ID mapping at the boundary; guard non-integer IDs (not-found, not crash).
4. Update imports/types in `main.py`, `auth_funcs.py`, `sim_funcs.py`; drop `bson`. Move the in-Python timeseries date filter (`main.py:305-318`) into SQL: `WHERE sim_id=%s AND time BETWEEN %s AND %s ORDER BY time`.

**Success criteria**
- API starts, pool opens/closes cleanly.
- CRUD round-trips preserve current JSON shapes; IDs appear as strings.
- Upserts are idempotent; `delete_model` cascades via FK; unknown user → 404.

**Verification (independent of the sim engine)**
- Endpoints not needing the sim subprocess, via `curl`:
```bash
curl -X POST "http://localhost:8000/workspace/models/submit-model?user_id=mvp-user" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"mvp-user","model_name":"t","location":"Berlin","roof_incl":30,"roof_azimuth":0,"electr_cons":3500,"peak_power":5,"battery_cap":5}'
curl "http://localhost:8000/workspace/models/fetch-models?user_id=mvp-user"    # array incl. new model, ids as strings
curl -X DELETE "http://localhost:8000/workspace/models/delete-model?user_id=mvp-user&model_id=<id>"
curl "http://localhost:8000/workspace/models/fetch-models?user_id=nobody"      # expect 404
```
- Throwaway `backend/scripts/smoke_db.py` (remove after) that calls each `Database` method directly — including typed upserts for `simulations`, `sim_results_eval`, `finances`, `fin_results` with sample payloads — asserting round-trip equality and idempotent re-upsert. Run: `docker compose run --rm backend python -m scripts.smoke_db`.
- Cascade check: after inserting a model + child rows via the smoke script, delete the model and confirm `SELECT count(*)` on each child table = 0.

*Deferred:* full `run-sim` / `fetch-sim-results` verification → Stage 6 (needs the ported sim engine).

---

### Stage 4 — Sim engine client (sync psycopg)

**Prerequisites:** Stages 1–2. Uses SQL fixtures (below) to stay independent of Stages 3 & 5.

**Steps**
1. Rewrite `backend/src/sim/ferntree/components/database/mongodb.py` as a sync `psycopg.Connection` client reading `DATABASE_URL`, keeping the class/method names used by callers:
   - `load_config()` — SELECT the `simulations` row; reassemble the config dict the sim expects (including `t_amb`/`g_i` arrays and flattened `system_settings`).
   - `get_load_profile(profile_id)` — SELECT `load_profile` array.
   - `__init__` — ensure the `simulations` results context; `DELETE FROM sim_timesteps WHERE sim_id=%s` (re-run replacement).
   - `write_batch(batch)` — `COPY sim_timesteps(...) FROM STDIN` (see §5), keeping the 1000-row buffer.
   - `shutdown()` — flush buffer + close connection.
2. Point the sim engine's env loading at `DATABASE_URL`.

**Success criteria**
- Running the sim engine populates `sim_timesteps` with the expected row count.
- Re-running the same `sim_id` replaces (not appends) rows.

**Verification (with SQL fixtures)**
```bash
# 1) seed a minimal fixture via psql: one models row, one simulations row
#    (small t_amb/g_i arrays + settings), one loadprofiles row (small array).
#    Capture the returned ids for --sim_id / --model_id.
docker compose exec postgres psql -U ferntree -d ferntree_db -c "INSERT INTO ... RETURNING id;"

# 2) run the engine directly
docker compose run --rm backend python src/sim/ferntree/ferntree.py --sim_id <sim_id> --model_id <model_id>   # exit 0

# 3) assert rows
docker compose exec postgres psql -U ferntree -d ferntree_db -c "SELECT count(*) FROM sim_timesteps WHERE sim_id=<sim_id>;"

# 4) re-run and confirm count unchanged (replaced, not doubled)
docker compose run --rm backend python src/sim/ferntree/ferntree.py --sim_id <sim_id> --model_id <model_id>
docker compose exec postgres psql -U ferntree -d ferntree_db -c "SELECT count(*) FROM sim_timesteps WHERE sim_id=<sim_id>;"
```

---

### Stage 5 — Reference data & cleanup scripts

**Prerequisites:** Stages 1–2.

**Steps**
1. Port `backend/src/sim/loadprofiles/alpg_profiles.py` and `pipeline_gold.py`: replace `insert_many`/`create_index` with Postgres inserts into `loadprofiles` (`load_profile` as `DOUBLE PRECISION[]`, `ON CONFLICT (profile_id) DO UPDATE`); read `DATABASE_URL`.
2. Port `backend/src/clean_database.py` to `TRUNCATE <tables> RESTART IDENTITY CASCADE`, aligning to the real table names (the current script references stale names `model_specs`/`sim_evaluation`/`sim_timeseries`).

**Success criteria**
- Loaders populate `loadprofiles` with the expected number of profiles; each array non-empty.
- Cleanup script empties tables without FK errors.

**Verification**
```bash
docker compose run --rm backend python src/sim/loadprofiles/alpg_profiles.py   # or relevant entrypoint
docker compose exec postgres psql -U ferntree -d ferntree_db -c "SELECT count(*) FROM loadprofiles;"
docker compose exec postgres psql -U ferntree -d ferntree_db -c "SELECT profile_id, array_length(load_profile,1) FROM loadprofiles LIMIT 5;"
# cleanup:
docker compose run --rm backend python src/clean_database.py
docker compose exec postgres psql -U ferntree -d ferntree_db -c "SELECT count(*) FROM models;"   # 0
```

---

### Stage 6 — End-to-end verification & Mongo removal

**Prerequisites:** Stages 1–5.

**Steps**
1. Remove all remaining Mongo remnants: imports, `certifi`, `ServerApi`, `ObjectId`, stale references; delete the throwaway `scripts/smoke_db.py`.
2. Run the full stack and exercise the real user flow (frontend or `curl`).
3. (Optional, recommended) Add a couple of `pytest` smoke tests for the data layer.

**Success criteria**
- Complete happy path works against Postgres with unchanged API contracts.
- Re-running a simulation replaces prior results (stable `sim_id`).
- No Mongo symbols remain in `backend/`.

**Verification**
```bash
docker compose up -d
# Full flow (via frontend or curl): submit-model -> run-sim -> fetch-sim-results
#  -> fetch-sim-timeseries (confirm SQL range filter + shape) -> submit-fin-form-data
#  -> fetch-fin-results -> delete-model.
# Re-run run-sim for the same model; confirm results replaced:
docker compose exec postgres psql -U ferntree -d ferntree_db -c "SELECT count(*) FROM sim_timesteps WHERE sim_id=<id>;"  # stable
# Delete cascade check: after delete-model, all child tables for that model -> 0 rows.
# No Mongo symbols remain:
rg -i "mongo|motor|pymongo|bson|objectid|certifi|serverapi" backend/    # no matches
```
- Diff a saved sample of each endpoint's JSON against pre-migration shapes → identical.

---

## 9. Risks & tradeoffs (carry forward)

- **Async pool lifecycle** must open/close with the app (FastAPI lifespan). Mis-wiring causes connection leaks or startup failures.
- **Normalized upserts** for `sim_results_eval`/`fin_results` are multi-statement transactions (more code; gains atomicity).
- **Large arrays** (`t_amb`, `g_i`, `load_profile`) as `DOUBLE PRECISION[]` — pragmatic exception to strict normalization; fine because they are always read/written whole.
- **No migration framework** — `schema.sql` only; future schema changes are manual. `initdb.d` runs only on an empty volume (use `down -v` or manual `psql` to re-apply).
- **loadprofiles must be seeded** (Stage 5) or simulations fail on the empty greenfield DB.
- **Users descoped** — every request maps to the single `mvp-user`; reintroducing real auth is future work.
- **Wins:** FK `ON DELETE CASCADE` replaces the fragile manual cascade; real transactions make result writes atomic; SQL range queries replace in-Python timeseries filtering; `COPY` is faster than the Mongo `$push` array append; the re-run bug (§7) is fixed.
```
