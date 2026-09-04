# Architecture A: Design Principles

This document describes the principles behind the Architecture A refactor: a
modular monolith with explicit internal boundaries. It is intended to guide
implementation decisions, not prescribe one exact directory layout.

The goal is to improve cohesion, testability, and responsiveness without
introducing distributed-system complexity before it is needed. The application
remains one deployable FastAPI service and one PostgreSQL database. The
simulation engine becomes an explicit internal module and the API remains
responsive while it runs.

## Target Mental Model

Think in terms of four responsibilities:

```text
HTTP request
    -> API / transport
    -> application orchestration
    -> domain logic
    -> persistence
```

This is a modular monolith, not a collection of microservices. Modules have
clear responsibilities and dependency directions, but they still run in the
same Python process and can be deployed together.

The most important dependency rule is:

```text
API may call application and domain code.
Domain code may use explicitly supplied infrastructure interfaces.
Persistence code knows about PostgreSQL, but not HTTP.
```

Avoid letting lower-level modules import upward. For example, the simulation
engine should not import FastAPI routers, and a repository should not return an
HTTP response.

## 1. Layered Architecture

### General principle

Separate code by responsibility. A typical layered arrangement is:

- **Transport layer:** HTTP routes, request parsing, response serialization,
  and HTTP-specific errors.
- **Application layer:** use-case orchestration, such as "run a simulation"
  or "calculate financial results".
- **Domain layer:** simulation, financial, and energy calculations that express
  the application's actual behavior.
- **Persistence/infrastructure layer:** PostgreSQL, external APIs, pools,
  environment configuration, and other technical details.

### When it makes sense

Layering helps when one file currently handles several kinds of work or when a
change in one concern routinely requires edits in unrelated concerns. It is
particularly useful when you want to test calculations without starting a web
server or test routes without requiring a real database.

### Benefits

- Makes the system easier to navigate.
- Localizes changes.
- Makes unit tests less dependent on HTTP and PostgreSQL.
- Gives future extraction into a worker or service a clearer seam.

### Costs and cautions

- More modules and indirection.
- Python does not enforce dependency direction automatically.
- A small use case can become over-engineered if every function is wrapped in
  several abstractions.

Use layers to separate meaningful responsibilities, not to maximize the number
of files.

### Repository location

The main locations are:

- `backend/src/api/` for transport modules.
- `backend/src/domains/` for simulation and calculation logic.
- `backend/src/db/` for database infrastructure and repositories.
- `backend/src/workers/` for execution boundaries around long-running work.
- `backend/src/main.py` for application composition.

The existing `solar_data/` code is also infrastructure because it calls
external services. Financial and energy KPI calculations belong with the
domain/application code rather than in route handlers.

## 2. Repository Pattern

### General principle

A repository encapsulates data access behind methods expressed in application
terms. Callers ask for operations such as `fetch_model_by_id` or
`upsert_fin_results`; they do not construct SQL or manage cursors.

The existing `Database` class is already a repository-like object. It should be
split into cohesive repositories rather than replaced with a large abstraction
framework.

### When it makes sense

Use repositories when database access is substantial, repeated, or mixed into
other responsibilities. They are especially useful when multiple use cases
need the same query or when tests should substitute database access.

Do not use the repository pattern merely because it is fashionable. A tiny
application with one query may be clearer with the query next to its use case.
In this project, the 782-line `Database` class and its mixed model,
simulation, and finance responsibilities justify the split.

### Benefits

- SQL and cursor management stay in a known layer.
- Database operations become easier to find and test.
- Ownership checks and transaction boundaries have an explicit home.
- A future simulation worker can take the simulation persistence operations
  without importing the API layer.

### Costs and cautions

- A repository can become a passive wrapper that adds no useful boundary.
- A clean method name can hide an inefficient query or an accidental N+1
  access pattern.
- Repositories should not contain unrelated business decisions. Keep domain
  calculations outside them.

### Repository location

Use `backend/src/db/repositories/`, with cohesive modules such as:

- `models_repo.py` for model creation, retrieval, update, and deletion.
- `simulation_repo.py` for simulation inputs, timesteps, and evaluated
  simulation results.
- `finance_repo.py` for finance inputs, financial results, and yearly data.

Shared database helpers can live in `base.py`, but avoid making `base.py` a
second god-class. A shared helper is appropriate for parsing IDs and asserting
model ownership; unrelated queries are not.

## 3. Aggregate and Transaction Boundaries

### General principle

Group data and operations around things that change together and share an
invariant. This is an aggregate boundary. It is usually a better repository
boundary than "one repository per table."

### Application of the principle

The parent and child records in these operations form one unit:

- `sim_results_eval` and its `pv_monthly_gen` rows.
- `fin_results` and its `fin_yearly_data` rows.

Their upsert and child-row replacement must remain in one transaction. Splitting
the tables into separate repositories should not split the operation or its
transaction boundary.

### Benefits

- Preserves consistency when an operation updates multiple tables.
- Gives each repository a meaningful domain boundary.
- Makes concurrency and failure behavior easier to reason about.

### Costs and cautions

- Aggregate boundaries require judgment.
- An aggregate that is too large creates coupling and long transactions.
- An aggregate that is too small makes invariants difficult to enforce.

The schema may remain normalized and the existing `schema.sql` remains the
database definition. Aggregate boundaries are an application design concept,
not a request to denormalize the SQL schema.

## 4. APIRouter Modules and Vertical Cohesion

### General principle

FastAPI's `APIRouter` groups related routes into modules. The routes remain
ordinary HTTP endpoints with the same URLs and behavior; only their source
organization changes.

For example, model routes belong together, as do simulation routes and finance
routes. A router should primarily translate HTTP input into a use-case call and
translate the result into an HTTP response.

### When it makes sense

Use routers when a single application has multiple domains or when the main
module is becoming a list of unrelated handlers. This project already has
natural model, simulation, and finance groups.

### Benefits

- Smaller, more navigable route modules.
- Feature-oriented ownership of endpoints.
- Shared prefixes and tags can be declared once.
- `main.py` becomes a readable application assembly point.

### Costs and cautions

- Splitting files does not automatically improve architecture.
- Keep business logic out of routers; otherwise the same monolith is spread
  across several files.
- Apply authentication, error handling, and dependency wiring consistently.

### Repository location

Use `backend/src/api/`, for example:

- `models_router.py` for `/workspace/models/...` routes.
- `simulations_router.py` for `/workspace/simulations/...` routes.
- `finances_router.py` for `/workspace/finances/...` routes.

`backend/src/main.py` should create the app, configure lifespan behavior, and
include these routers.

## 5. Dependency Injection and Dependency Inversion

### General principle

High-level code should declare what it needs rather than construct technical
dependencies internally. The caller or composition root supplies repositories,
configuration, and services.

Dependency inversion does not mean every class needs an interface. It means the
important policy code does not reach directly into global pools, environment
variables, or HTTP framework state when those dependencies can be supplied.

FastAPI's dependency system is one mechanism for this. Plain Python constructor
arguments are another, and are often simpler for domain code.

### Benefits

- Route tests can inject fake repositories.
- Domain tests can run without FastAPI or PostgreSQL.
- Resource ownership and lifecycle are easier to see.
- Later extraction into a worker is less coupled to the API process.

### Costs and cautions

- Dependency wiring adds indirection.
- Too many protocols, factories, or generic providers obscure simple code.
- A module-level pool can be practical, but its lifecycle must be explicit and
  it should not be accessed unpredictably throughout the codebase.

### Repository location

Wire dependencies in `backend/src/main.py` and API modules. Keep the pool and
repository construction in the database/infrastructure area. Pass domain
dependencies into application functions rather than importing the FastAPI app
from domain code.

## 6. Explicit Python Package Boundaries

### General principle

Modules should be importable by their real package path. Avoid modifying
`sys.path`, relying on the current working directory, or dynamically importing
bare module names to make a component work.

### Application to the simulation engine

The current engine uses `sys.path.insert`, `importlib.import_module("sim_builder")`,
and imports such as `from components...`. These mechanisms hide the engine's
real dependencies and make in-process reuse fragile.

The simulation package should have an explicit public entry point, for example
`build_and_run_simulation(sim_id, model_id)`, while its internal modules use
normal package imports. Internal implementation details should not become the
API's responsibility.

### Benefits

- Import paths are deterministic.
- Hidden load-order and working-directory assumptions disappear.
- The engine can be tested and called by a future worker.
- Package ownership is visible in code review.

### Costs and cautions

- Existing implicit imports may reveal circular dependencies.
- Moving a package can require updating tests, scripts, and documentation.
- Keep the public entry point small; do not expose every engine class as a
  supported integration API.

### Repository location

The engine belongs under `backend/src/domains/simulation/` if that is the
chosen target layout. Give the package a deliberate public entry point and
keep CLI argument parsing in a thin CLI adapter if the CLI is retained.

## 7. Non-Blocking Execution Boundaries

### General principle

An async event loop must not execute long synchronous or CPU-bound work
directly. Put a clear boundary around expensive simulation work and run it in a
thread or process executor, or eventually in a separate worker service.

### Application to this repo

`run_ferntree_simulation` is declared `async`, but currently calls synchronous
`subprocess.run`. The declaration does not make the subprocess call non-
blocking. While it runs, the FastAPI event loop cannot serve other work.

The engine is synchronous and uses a synchronous PostgreSQL client, so it is
reasonable for the execution boundary to call it synchronously from an
executor. The API-facing code can remain async.

### Benefits

- Other API requests remain serviceable during a simulation.
- The boundary makes timeout and failure handling explicit.
- The same runner can later be moved into a queue consumer or worker
  container.

### Costs and cautions

- Threads and processes introduce concurrency and lifecycle concerns.
- Exceptions, cancellation, and partial database output need defined behavior.
- A background task is not a durable job system: process crashes can lose work.
- CPU-heavy work generally benefits more from a process than a thread, but
  measure the actual workload and account for process startup and memory use.

### Repository location

Put the execution adapter in `backend/src/workers/sim_runner.py`. It should
bridge the API/application layer to the simulation package. It should not own
simulation algorithms, and it should not contain route definitions.

Whether the API waits for completion or returns immediately with a pollable
status is a separate product/API decision. Non-blocking execution and
asynchronous client-visible job semantics are related, but they are not the
same thing.

## 8. Application Factory and Composition Root

### General principle

Have one obvious place where the application is assembled: create the FastAPI
app, register routers, configure lifespan, and connect infrastructure
dependencies.

This is the composition root. Components should define behavior; the
composition root decides which concrete implementations and resources they use.

### Benefits

- The system's wiring is visible in one place.
- Connection-pool startup and shutdown remain explicit.
- Tests can construct a smaller application or replace dependencies.
- Importing a module does not unexpectedly open a database connection.

### Costs and cautions

- The composition root can become a new dumping ground.
- Keep business logic and SQL out of it.
- Configuration should be loaded deliberately rather than as a surprising
  import-time side effect.

### Repository location

Use `backend/src/main.py` for app assembly and lifespan. Keep database pool
creation/configuration in the database infrastructure package, but let app
lifecycle control when the pool opens and closes.

## 9. Preserve Security and Transaction Invariants

Refactoring changes locations, not behavior. Two classes of behavior deserve
explicit protection:

### Ownership checks

The current API verifies that a model belongs to the requesting user through
`_assert_model_owner` and SQL joins against `users`. Every repository operation
that accepts a user identity must preserve equivalent authorization behavior.
Do not treat moving SQL as permission to remove or weaken these checks.

### Transaction boundaries

Operations that replace a parent row and its child rows must remain atomic. In
particular, the simulation evaluation and financial result upserts should not
leave half-written child data if an insert fails.

These are architectural invariants, not implementation details. Tests should
make them visible.

## 10. Keep Database DDL Separate from Pydantic Models

`backend/schema.sql` and Python/Pydantic models serve different purposes:

- `schema.sql` defines PostgreSQL tables, constraints, indexes, and seed data.
- Pydantic models validate API payloads and serialize Python values.

They should not be merged into one file or treated as interchangeable schema
definitions. PostgreSQL is currently initialized by mounting `schema.sql` into
the Postgres container's `/docker-entrypoint-initdb.d/` directory. The
Architecture A refactor should preserve that behavior.

Pydantic DTOs may be reorganized for clarity, but that does not replace the SQL
DDL or database initialization process.

## Decision Test

When uncertain during the refactor, ask:

1. Does this change establish a meaningful boundary or only add indirection?
2. Is the dependency direction still transport/application/domain/
   infrastructure?
3. Did I preserve ownership checks, transaction boundaries, and public API
   behavior?
4. Can the affected logic be tested without starting unrelated components?
5. Would this boundary make a future simulation worker easier to extract?

If the answer to the first question is no, prefer the simpler design.
