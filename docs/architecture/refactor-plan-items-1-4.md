# Refactor Implementation Plan: Work Items 1-4

## Purpose

This plan implements four architectural fixes identified against
`docs/architecture/principles.md`:

1. DI purity via narrow, domain-owned protocols.
2. Composition-root wiring instead of a module-level database singleton.
3. Removal of `HTTPException` from the domain layer.
4. Consolidation and clearer naming of the asynchronous and synchronous database clients.

This plan is based on the guiding principles only. Do not read
`docs/architecture/cheat-sheet.md`; it contains deliberate deviations from the
current plan.

All paths are relative to the repository root `/workspaces/ferntree`. Backend
source files are under `backend/src`, and backend tests are under
`backend/tests`.

Test coverage for the new protocols, router error translation, and moved client
is intentionally deferred to a later stage. Existing tests should still be
run where their prerequisites are available.

## Recommended Order

Implement the work items in this order:

1. Item 3: remove the domain-layer `HTTPException` dependency.
2. Item 1: introduce narrow domain protocols.
3. Item 2: move database-client construction to the composition root.
4. Item 4: consolidate the async and sync database clients under `db/`.

Items 1 and 3 both touch `domains/finances/funcs.py`; implement them carefully
or combine those edits in one pass.

## Current State

### Database clients and configuration

- `backend/src/db/client.py` defines `DatabaseClient` as a multiple-inheritance
  facade over `ModelsRepository`, `SimulationRepository`, and `FinanceRepository`.
- `backend/src/db/pool.py` creates the module-level asynchronous
  `AsyncConnectionPool` named `pool`.
- `backend/src/db/pool.py` also loads `.env` and reads `DATABASE_URL` at import
  time.
- `backend/src/api/dependencies.py` creates a module-level
  `db_client = DatabaseClient()`.
- `backend/src/api/main.py` opens and closes the async pool in the FastAPI
  lifespan, registers the routers, and configures CORS.
- `backend/src/domains/ferntree/components/database/postgres.py` defines the
  synchronous `PostgresClient` used by the simulation engine.
- The sync client independently loads `.env` by walking a relative path:
  `../../../../../.env`.

### Domain functions

- `backend/src/domains/energy/funcs.py::eval_sim_results` imports and accepts
  the concrete `DatabaseClient`, but only calls `fetch_timesteps`.
- `backend/src/domains/finances/funcs.py::calc_fin_results` imports and accepts
  the concrete `DatabaseClient`, but only calls `fetch_model_by_id` and
  `fetch_sim_results_eval`.
- `calc_fin_results` currently imports FastAPI and raises `HTTPException` when
  simulation results are missing.

### Sync engine references

- `backend/src/domains/ferntree/sim_builder.py` imports and constructs
  `PostgresClient(sim_id, model_id)`.
- `backend/src/domains/ferntree/components/host/sim_host.py` imports
  `PostgresClient` for a type annotation.
- `backend/src/domains/ferntree/components/database/models.py` contains the
  Pydantic `TimestepData` and `LoadProfile` models used by the engine database
  code. These models must move with the sync database infrastructure so that
  `db/` does not import upward from `domains/ferntree`.

### Relevant repository signatures

```python
async def fetch_timesteps(
    self,
    model_id: str,
    user_id: str,
    start: Optional[float] = None,
    end: Optional[float] = None,
    limit: Optional[int] = None,
) -> list[dict[str, float]]

async def fetch_model_by_id(
    self, model_id: str, user_id: str
) -> ModelDataOut

async def fetch_sim_results_eval(
    self, model_id: str, user_id: str
) -> Optional[SimResultsEval]
```

## Item 3: Remove `HTTPException` From the Domain Layer

### Goal

Domain code must not depend on FastAPI or HTTP response semantics. The domain
should raise a standard Python error, and the router should translate that
error into an HTTP response.

### Error choice

Use the standard `RuntimeError`. Do not add a custom exception type. This is
consistent with the existing `eval_sim_results` behavior and keeps the change
small.

### Implementation steps

1. Open `backend/src/domains/finances/funcs.py`.
2. Remove:

   ```python
   from fastapi import HTTPException, status
   ```

3. Replace the missing-results branch in `calc_fin_results`:

   ```python
   if sim_results_eval is None:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="Simulation results not found.",
       )
   ```

   with:

   ```python
   if sim_results_eval is None:
       raise RuntimeError(
           f"Simulation results not found for model {model_data.model_id}"
       )
   ```

4. Update the `Raises` section of the `calc_fin_results` docstring from
   `HTTPException` to `RuntimeError`.
5. Open `backend/src/api/routers/finances_router.py`.
6. Around the call to `calc_fin_results` in `submit_fin_form_data`, translate
   the domain error at the transport boundary:

   ```python
   try:
       fin_results: FinResults = await calc_fin_results(
           db_client, fin_form_data_sub, user_id
       )
   except RuntimeError as error:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="Simulation results not found.",
       ) from error
   ```

7. Keep the subsequent `upsert_fin_results` call unchanged.
8. Preserve the existing external behavior: submitting financial data without
   evaluated simulation results should still result in HTTP 404.

### Verification

- Search `backend/src/domains/` for `fastapi`; there should be no domain-layer
  FastAPI import.
- Confirm `finances_router.py` remains responsible for translating the missing
  simulation-results failure into a 404 response.
- Do not add tests in this stage; test coverage is deferred.

## Item 1: DI Purity Through Narrow Protocols

### Goal

Domain policy code should declare the small persistence capabilities it needs,
without importing the concrete `DatabaseClient`. Each consuming domain package
owns its own protocol. `DatabaseClient` remains the production implementation
and satisfies the protocols structurally.

### Energy protocol

1. Create `backend/src/domains/energy/ports.py`.
2. Add a narrow `TimestepReader` protocol containing only the operation used by
   `eval_sim_results`:

   ```python
   from typing import Optional, Protocol


   class TimestepReader(Protocol):
       """Read-side persistence interface required by energy evaluation."""

       async def fetch_timesteps(
           self,
           model_id: str,
           user_id: str,
           start: Optional[float] = None,
           end: Optional[float] = None,
           limit: Optional[int] = None,
       ) -> list[dict[str, float]]: ...
   ```

   Include the optional arguments so the protocol matches the concrete
   repository method and remains useful if the domain later requests a range.

3. Open `backend/src/domains/energy/funcs.py`.
4. Remove the import of `DatabaseClient`.
5. Import `TimestepReader` from `src.domains.energy.ports`.
6. Change the `eval_sim_results` parameter annotation from `DatabaseClient` to
   `TimestepReader`. Prefer the parameter name `db` or `reader` to make the
   dependency's capability clear.
7. Update the call from `db_client.fetch_timesteps(...)` to the new parameter
   name and update the docstring accordingly.

### Finance protocol

1. Create `backend/src/domains/finances/ports.py`.
2. Define `FinanceDataReader` with only the two methods used by
   `calc_fin_results`:

   ```python
   from typing import Optional, Protocol

   from src.db.schemas import ModelDataOut, SimResultsEval


   class FinanceDataReader(Protocol):
       """Read-side persistence interface required by financial calculation."""

       async def fetch_model_by_id(
           self, model_id: str, user_id: str
       ) -> ModelDataOut: ...

       async def fetch_sim_results_eval(
           self, model_id: str, user_id: str
       ) -> Optional[SimResultsEval]: ...
   ```

3. Open `backend/src/domains/finances/funcs.py`.
4. Remove the import of `DatabaseClient`.
5. Import `FinanceDataReader` from `src.domains.finances.ports`.
6. Change the `calc_fin_results` parameter annotation from `DatabaseClient` to
   `FinanceDataReader`.
7. Update the two repository calls to use the renamed parameter and update the
   docstring.

### Integration expectations

- Do not change `DatabaseClient`, the repositories, or router dependency
  signatures for this item.
- Routers may continue passing the concrete `DatabaseClient`; structural typing
  means it provides the methods required by each protocol.
- Do not create one broad shared protocol for the entire database client. The
  protocol should remain as narrow as the consuming function's needs.

### Verification

- Search `backend/src/domains/` for `src.db.client`; there should be no domain
  import of the concrete `DatabaseClient`.
- Confirm the protocol method names and return types match the repositories.
- Do not add protocol unit tests in this stage; test coverage is deferred.

## Item 2: Composition Root Instead of Module-Level Singleton

### Goal

Construct `DatabaseClient` in the application composition root and expose it
through `app.state`. Remove the module-level `DatabaseClient()` from
`api/dependencies.py` while preserving the existing FastAPI dependency
signatures used by the routers.

### Implementation steps

1. Open `backend/src/api/main.py`.
2. Import:

   ```python
   from src.db.client import DatabaseClient
   ```

3. Change the lifespan signature from:

   ```python
   async def lifespan(_: FastAPI):
   ```

   to:

   ```python
   async def lifespan(app: FastAPI):
   ```

4. After opening the pool, construct the client and store it on app state:

   ```python
   await pool.open()
   app.state.db_client = DatabaseClient()
   ```

5. Keep pool shutdown in the existing `finally` block. The `DatabaseClient`
   itself is currently a lightweight facade over the pool and has no close
   method; the pool remains the resource whose lifecycle must be managed.
6. Update the lifespan docstring to describe the `app` argument rather than
   `_`.
7. Open `backend/src/api/dependencies.py`.
8. Remove:

   ```python
   db_client: DatabaseClient = DatabaseClient()
   ```

9. Import `Request` from FastAPI.
10. Change `get_db_client` to read the app-scoped client:

    ```python
    def get_db_client(request: Request) -> DatabaseClient:
        """Return the application database client from app state."""
        return request.app.state.db_client
    ```

11. Leave `check_user_exists` unchanged apart from any formatting needed. It
    already receives its client through `Depends(get_db_client)`.
12. Leave all routers unchanged. They already use
    `Depends(get_db_client)`.
13. Leave `backend/tests/test_data_layer.py` unchanged. Its direct
    `DatabaseClient()` construction is a data-layer test fixture, not the
    application composition path.

### Verification

- Search for direct imports of a removed `db_client` symbol from
  `api.dependencies`; none should remain.
- Search for `DatabaseClient()` construction. Production construction should be
  in `api/main.py`; direct construction in the data-layer test fixture is
  expected.
- Confirm that the app lifespan sets `app.state.db_client` before requests can
  resolve `get_db_client`.
- Import the app from the backend directory with
  `python -c "import src.api.main"`.
- Do not add composition-root tests in this stage; test coverage is deferred.

## Item 4: Consolidate Async and Sync Database Infrastructure

### Goal

Keep both database clients, because the API is async and the synchronous
simulation engine runs behind an execution boundary, but make their ownership
and naming explicit:

```text
backend/src/db/
  config.py          # the single DATABASE_URL/configuration loader
  async_client.py    # async PostgreSQL pool
  sync_client.py     # synchronous PostgreSQL client used by the engine
  sync_models.py     # Pydantic models required by sync persistence
```

The `db/` package must not import upward from `domains/ferntree`. Therefore the
sync persistence models move out of the engine package with the sync client.
The engine may import downward from `db/`.

### Step 1: Create the single configuration module

Create `backend/src/db/config.py`:

```python
import os

from dotenv import load_dotenv

load_dotenv("./.env")
DATABASE_URL: str = os.environ["DATABASE_URL"]
```

This is the only module in the new database client arrangement that loads the
environment and reads `DATABASE_URL`.

Do not add another relative path walk based on the importing file's location.
The application/runtime should provide the expected `.env` location or
environment variable deliberately.

### Step 2: Rename the async client module

1. Rename `backend/src/db/pool.py` to `backend/src/db/async_client.py`.
2. Remove its `os` and `dotenv` imports and local environment loading.
3. Import the shared configuration:

   ```python
   from psycopg_pool import AsyncConnectionPool

   from src.db.config import DATABASE_URL
   ```

4. Keep the public pool object and its current lifecycle configuration:

   ```python
   pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False)
   ```
5. Update every import of `from src.db.pool import pool` to
   `from src.db.async_client import pool` in:
   - `backend/src/db/repositories/base.py`
   - `backend/src/db/repositories/models_repo.py`
   - `backend/src/db/repositories/simulation_repo.py`
   - `backend/src/db/repositories/finance_repo.py`
   - `backend/src/api/main.py`
   - `backend/tests/test_data_layer.py`

### Step 3: Move sync persistence models

1. Create `backend/src/db/sync_models.py`.
2. Move/copy the definitions of `TimestepData` and `LoadProfile` from
   `backend/src/domains/ferntree/components/database/models.py` into the new
   file without changing their fields or validation behavior.
3. Check all uses of `LoadProfile`. If it is only part of the database model
   module and not used elsewhere, it may still be moved as part of this
   database-infrastructure consolidation; do not remove it without checking
   imports.
4. The new `db/sync_models.py` must not import from `domains/ferntree`.

### Step 4: Move and rename the sync client

1. Create `backend/src/db/sync_client.py` from the implementation currently in
   `backend/src/domains/ferntree/components/database/postgres.py`.
2. Remove the sync client's `os`, `load_dotenv`, `script_dir`, and relative-path
   configuration code.
3. Import the shared URL:

   ```python
   from src.db.config import DATABASE_URL
   ```

4. Import `TimestepData` from:

   ```python
   from src.db.sync_models import TimestepData
   ```

5. Preserve the `PostgresClient` class name, constructor signature, query
   behavior, batching, commits, and shutdown behavior. In particular, preserve
   the constructor's existing deletion of prior `sim_timesteps` rows.
6. Update the class docstring from referring to a subprocess to describing the
   synchronous client used by the in-process simulation executor.

### Step 5: Update engine imports

1. In `backend/src/domains/ferntree/sim_builder.py`, replace the old import:

   ```python
   from src.domains.ferntree.components.database.postgres import PostgresClient
   ```

   with:

   ```python
   from src.db.sync_client import PostgresClient
   ```

2. In `backend/src/domains/ferntree/components/host/sim_host.py`, make the same
   import change. It is used for the `PostgresClient` type annotation.
3. Do not move simulation algorithms or route logic into `db/`; only the sync
   persistence client and its persistence models move.

### Step 6: Remove obsolete engine database files

1. Verify there are no remaining imports of
   `src.domains.ferntree.components.database.postgres` or
   `src.domains.ferntree.components.database.models`.
2. Delete `backend/src/domains/ferntree/components/database/postgres.py`.
3. Delete `backend/src/domains/ferntree/components/database/models.py` after
   confirming both models were moved and no imports remain.
4. Leave `backend/src/domains/ferntree/components/database/mongodb.py` alone.
   Its cleanup is outside this work item.

### Verification

- Search for `components.database.postgres`; no source import should remain.
- Search for `from src.db.pool import`; no source or test import should remain.
- Search `backend/src/db` for `from src.domains.ferntree`; there should be no
  upward engine dependency.
- Search for `load_dotenv` and `DATABASE_URL`; the new database client path
  should load configuration only through `src.db.config`.
- Import the app from `backend/` with
  `python -c "import src.api.main"`.
- Run `pytest tests/test_simulation_runner.py` from `backend/`.
- Run `pytest tests/test_data_layer.py` only when PostgreSQL is available.
  This test requires a live database.
- Do not add new tests for the relocation in this stage; test coverage is
  deferred.

## Global Verification

Run these checks from `/workspaces/ferntree/backend` after all four items:

```bash
grep -rn "fastapi" src/domains/
grep -rn "src.db.client" src/domains/
grep -rn "from src.db.pool import" src tests
grep -rn "components.database.postgres" src tests
grep -rn "from src.domains.ferntree" src/db
python -c "import src.api.main"
pytest tests/test_simulation_runner.py
```

The first five searches should produce no matches. The import smoke test and
simulation-runner test should pass. The data-layer test is conditional on a
running PostgreSQL instance.

## Explicitly Out of Scope

- New tests for protocols, error translation, composition-root wiring, or the
  client relocation. These are deferred to a later testing stage.
- Items 5-8 from the earlier assessment, including argument-order cleanup,
  redundant ownership guards, dormant-code cleanup, and invariant-test work.
- Cleanup of `mongodb.py` or dormant heating modules.
