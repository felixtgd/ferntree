# Architecture A: Refactor Cheat Sheet

This is a practical implementation checklist for turning the current backend
into a modular monolith. It is intentionally more operational than
`principles.md`; use the principles to resolve decisions that are not covered
here.

## Target Shape

The exact names can vary, but the responsibilities should resemble this:

```text
backend/
├── schema.sql                         # PostgreSQL DDL and seed data
└── src/
    ├── main.py                        # FastAPI composition root
    ├── api/                           # HTTP transport
    │   ├── models_router.py
    │   ├── simulations_router.py
    │   └── finances_router.py
    ├── domains/
    │   └── simulation/                # importable Ferntree engine
    ├── db/
    │   ├── pool.py                    # pool/config lifecycle support
    │   ├── models.py                  # Pydantic DTOs, if retained here
    │   └── repositories/
    │       ├── base.py
    │       ├── models_repo.py
    │       ├── simulation_repo.py
    │       └── finance_repo.py
    ├── solar_data/                    # external solar/geolocation APIs
    ├── utils/                         # transitional shared orchestration
    └── workers/
        └── sim_runner.py              # non-blocking execution adapter
```

The directory names are suggestions. The boundaries and dependency direction
matter more than the names.

## Current-to-Target Map

| Current responsibility | Target responsibility |
|---|---|
| `src/main.py` routes | `src/api/*_router.py` |
| `src/main.py` app/lifespan | `src/main.py` composition root |
| `src/database/postgres.py` pool | `src/db/pool.py` |
| `src/database/postgres.py` `Database` methods | `src/db/repositories/*` |
| `src/database/models.py` | Pydantic DTO module, often `src/db/models.py` or `src/contracts/` |
| `src/utils/sim_funcs.py` subprocess launcher | `src/workers/sim_runner.py` plus application orchestration |
| `src/sim/ferntree/` | importable `src/domains/simulation/` package |
| `src/sim/ferntree/components/database/postgres.py` | engine's synchronous persistence adapter, kept specialized initially |
| `backend/schema.sql` | unchanged PostgreSQL initialization source |

## Phase 0: Establish a Baseline

- [ ] Record the current API paths and methods from `src/main.py`.
- [ ] Confirm the frontend-visible response shapes and string ID behavior.
- [ ] Run the existing test suite before changing imports.
- [ ] Run a known simulation and verify that it writes `sim_timesteps`.
- [ ] Verify that financial results and simulation evaluation can be fetched.
- [ ] Inspect `git status` and avoid overwriting unrelated worktree changes.

Useful commands from the repository root:

```bash
pytest
docker compose up --build
```

Do not use the baseline only as a formality. If behavior changes later, you
need to know whether the refactor caused it.

## Phase 1: Separate HTTP Transport from Application Work

### Routes

- [ ] Create an `api/` package.
- [ ] Group model routes together.
- [ ] Group simulation routes together.
- [ ] Group finance routes together.
- [ ] Define an `APIRouter` in each module.
- [ ] Preserve the current public paths, HTTP methods, query parameters, and
      response models.
- [ ] Use router prefixes/tags only when they produce the same external URLs.
- [ ] Keep route functions thin: parse HTTP input, invoke a use case, return a
      result.
- [ ] Do not move SQL into router files.

### Application assembly

- [ ] Keep FastAPI app creation in `main.py`.
- [ ] Register each router with `app.include_router(...)`.
- [ ] Keep CORS and lifespan setup in the application assembly area.
- [ ] Ensure importing a router does not open a connection or start work.

### Checkpoint

- [ ] Open the generated OpenAPI document and compare paths/methods.
- [ ] Run route tests or exercise every endpoint manually.
- [ ] Confirm frontend URLs still work without frontend changes.

If this checkpoint fails, stop and fix route organization before changing the
database layer.

## Phase 2: Define Database Infrastructure and Repositories

### Pool and lifecycle

- [ ] Move pool configuration into a focused database infrastructure module,
      if that improves ownership and lifecycle clarity.
- [ ] Keep pool opening and closing under FastAPI lifespan control.
- [ ] Avoid reading environment variables in surprising domain-module import
      side effects.
- [ ] Keep one API-side async pool rather than creating connections per route.

### Split by aggregate, not merely by table

- [ ] Place model CRUD operations in a model repository.
- [ ] Place simulation input, timestep, and evaluated-result operations in a
      simulation repository.
- [ ] Place finance input, result, and yearly-data operations in a finance
      repository.
- [ ] Keep `sim_results_eval` with `pv_monthly_gen` operations that must be
      atomic.
- [ ] Keep `fin_results` with `fin_yearly_data` operations that must be
      atomic.
- [ ] Keep SQL in repository modules.
- [ ] Keep calculations out of repositories.

### Shared helpers

- [ ] Centralize safe ID parsing if multiple repositories need it.
- [ ] Centralize or consistently reuse model ownership assertions.
- [ ] Avoid turning a `base.py` helper into a second all-purpose database class.

### Repository interfaces

- [ ] Name methods after business operations, not SQL statements.
- [ ] Decide whether repositories receive a pool, a connection, or a database
      context, and use the choice consistently.
- [ ] Make transaction scope explicit for multi-table writes.
- [ ] Preserve string conversion at the API boundary if the frontend depends
      on string IDs.
- [ ] Preserve existing not-found and invalid-ID behavior unless intentionally
      changing the API contract.

### Checkpoint

- [ ] Run repository tests against a test database or controlled database
      fixture.
- [ ] Exercise model create/list/fetch/update/delete behavior.
- [ ] Exercise simulation input upsert and timestep retrieval.
- [ ] Exercise simulation evaluation plus monthly PV rows.
- [ ] Exercise finance input and finance result plus yearly rows.
- [ ] Verify a user cannot read or modify another user's model data.
- [ ] Verify a failed parent/child write does not leave partial child data.

## Phase 3: Rewire Application Services Without Changing Behavior

- [ ] Identify each route's use case before moving code.
- [ ] Keep external PVGIS and geolocation calls outside repositories.
- [ ] Keep financial calculations outside route functions and repositories.
- [ ] Keep energy KPI calculations outside route functions and repositories.
- [ ] Have application functions receive the repositories/services they need.
- [ ] Avoid making application code depend on `Request`, `Response`, or
      FastAPI exceptions unless that is an intentional boundary choice.
- [ ] Replace broad `Database` dependencies with focused repository
      dependencies where practical.
- [ ] Keep authentication/ownership behavior equivalent during the move.

### Checkpoint

- [ ] Verify a route can be tested with a fake repository or stub.
- [ ] Verify calculations can be tested without starting FastAPI.
- [ ] Verify repository code can be tested without importing route modules.
- [ ] Search for route modules importing raw SQL or domain modules importing
      FastAPI.

## Phase 4: Make Ferntree a Real Package

The current engine is functionally separate but import-path fragile. It uses
`sys.path.insert`, `importlib.import_module("sim_builder")`, and top-level
`components` imports. The target is an ordinary Python package with an
explicit public entry point.

### Package boundary

- [ ] Choose the final engine package location, such as
      `src/domains/simulation/`.
- [ ] Add `__init__.py` files where package imports require them.
- [ ] Expose one small public function for the application/worker to call,
      such as `build_and_run_simulation(sim_id, model_id)`.
- [ ] Keep CLI argument parsing in a thin adapter if the CLI remains useful.
- [ ] Keep simulation algorithms and component assembly inside the engine
      package.

### Imports

- [ ] Replace bare `sim_builder` imports with package imports.
- [ ] Replace `components...` imports with imports rooted in the simulation
      package.
- [ ] Remove the runtime `sys.path` mutation.
- [ ] Remove dynamic imports that exist only to compensate for the old path
      layout.
- [ ] Check for circular imports after each package boundary change.

### Engine persistence

- [ ] Keep the synchronous engine database client initially if its batched
      `COPY` writer is useful for timestep output.
- [ ] Remove fragile relative `.env` path assumptions.
- [ ] Make the engine receive configuration explicitly or use the same stable
      application configuration source.
- [ ] Keep engine persistence separate from the API's async pool unless there
      is a concrete reason to unify them.
- [ ] Ensure the engine still deletes/replaces prior results according to the
      current rerun semantics.

### Checkpoint

- [ ] Import the engine using its package path from a small test or Python
      shell.
- [ ] Run the public simulation entry point against a known model.
- [ ] Compare timestep count and representative values with the baseline.
- [ ] Confirm the engine works independently of the current working directory.
- [ ] Confirm no engine module mutates global `sys.path`.

## Phase 5: Add the Non-Blocking Simulation Runner

### Responsibility of `workers/sim_runner.py`

The runner is an execution adapter. It receives simulation identifiers,
invokes the importable engine, and controls how synchronous work is scheduled
relative to the async API. It is not another simulation domain layer.

- [ ] Define a small runner function with a clear success/failure contract.
- [ ] Call the simulation package's public entry point rather than reaching
      into engine internals.
- [ ] Run the synchronous engine through an executor so it does not execute on
      the FastAPI event loop.
- [ ] Choose thread or process execution deliberately. Consider CPU behavior,
      memory, startup cost, and database connection ownership.
- [ ] Do not pass an async database connection into synchronous engine code.
- [ ] Ensure database connections are created and closed in the execution
      context that uses them.
- [ ] Decide how exceptions, cancellation, timeouts, and partial output are
      represented.
- [ ] Log simulation ID, model ID, duration, and failure reason without
      logging sensitive data.

### API behavior decision

A non-blocking event loop does not automatically mean the HTTP request returns
immediately. Choose one contract deliberately:

- **Wait for completion off the event loop:** preserves current client
  behavior, but the HTTP request remains open.
- **Return a job/simulation status immediately:** requires explicit status
  state and client polling, but is more suitable for long simulations.

For Architecture A, either can be valid. Do not accidentally change the API
contract merely because the internal execution moved to an executor.

### Checkpoint

- [ ] Start a simulation.
- [ ] While it runs, issue another lightweight API request.
- [ ] Confirm the second request is serviced.
- [ ] Confirm simulation failures reach the intended API error/status path.
- [ ] Confirm successful output is readable by existing result endpoints.
- [ ] Test two simulations if concurrent execution is allowed; verify their
      database rows and timestep writes cannot be confused.

## Phase 6: Remove Transitional Coupling

- [ ] Remove the old subprocess launcher once the import path is verified.
- [ ] Remove obsolete `sim_funcs.py` imports and dead code.
- [ ] Remove obsolete `sys.path` and dynamic-import logic.
- [ ] Remove duplicated API database methods after all callers use repositories.
- [ ] Update tests and documentation to the final package paths.
- [ ] Update Docker commands only where paths genuinely changed.
- [ ] Keep `schema.sql` mounted and initialized by PostgreSQL as before.
- [ ] Do not add a migration framework solely because files moved.

## Dependency Direction Check

Use this as a quick import review:

```text
main.py
  -> api routers
  -> application/use-case functions
  -> domain modules
  -> repository/infrastructure implementations

simulation engine
  -> simulation components
  -> its explicit persistence adapter

repositories
  -> PostgreSQL driver and DTO/domain conversion

No lower layer should import an API router or FastAPI application.
```

Some shared contracts may be imported by multiple layers. That is acceptable
when they are genuinely passive data definitions. Avoid shared modules that
also perform I/O or initialize global resources.

## Common Traps

- [ ] Do not merge `schema.sql` with Pydantic models. SQL initializes the
      database; Pydantic validates Python/API data.
- [ ] Do not rename every concept at once. Names are less important than
      preserved behavior and clear boundaries.
- [ ] Do not split every table into a repository if operations span tables.
- [ ] Do not put business logic in route files just because they are now
      separate files.
- [ ] Do not assume `async def` makes synchronous code non-blocking.
- [ ] Do not use FastAPI `BackgroundTasks` as a durable job queue. It runs in
      the web process and work can be lost when that process exits.
- [ ] Do not share a live async connection or pool with synchronous executor
      code without verifying driver/thread/process rules.
- [ ] Do not remove ownership checks while moving SQL.
- [ ] Do not open database connections as a module import side effect.
- [ ] Do not introduce interfaces and factories where a constructor argument
      is enough.
- [ ] Do not optimize for a future microservice split at the expense of a
      coherent current monolith.

## Verification Matrix

| Area | Minimum verification |
|---|---|
| Routes | OpenAPI paths, methods, params, and response shapes unchanged |
| Models | CRUD and ownership checks work |
| Simulations | Input upsert, engine run, rerun replacement, and timestep reads work |
| Evaluation | KPI and monthly PV writes remain atomic and readable |
| Finances | Input/result/yearly-data flows remain atomic and readable |
| Engine imports | Runs through package entry point without path hacks |
| Event loop | Another API request succeeds during a simulation |
| Configuration | Compose startup and `DATABASE_URL` behavior remain correct |
| Tests | Unit tests cover domain logic; integration tests cover repository/API wiring |

## Definition of Done

- [ ] `main.py` is an application composition module, not a domain god-file.
- [ ] API routes are grouped by domain and remain thin.
- [ ] Database access is isolated in cohesive repositories.
- [ ] Ownership checks and multi-table transaction boundaries are preserved.
- [ ] The SQL database initialization path is unchanged and documented.
- [ ] The simulation engine imports through a real package boundary.
- [ ] Long-running simulation work does not block the FastAPI event loop.
- [ ] Existing endpoint behavior is verified.
- [ ] The final structure gives a future queue-backed simulation worker a clear
      extraction seam without pretending that Architecture A is already a
      distributed system.
