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

### Self-review questions

- **Which layer does each import come from?** Bad: a domain or infrastructure module imports transport code. Remedy: move the dependency to the owning layer or invert it through a lower-level interface.
- **Does a lower-level module import an upper-level module?** Bad: a domain module imports FastAPI or a repository imports a router. Remedy: keep dependencies directed from transport/application toward domain/infrastructure, never upward.
- **Does this module contain HTTP concepts outside the transport layer?** Bad: domain code raises `HTTPException` or depends on request objects. Remedy: raise a domain/application error and translate it to HTTP in the router.
- **Is business logic in a router?** Bad: a handler performs financial calculations or simulation decisions. Remedy: keep the router as an HTTP adapter and move orchestration to application code or calculations to the domain.
- **If an import arrow points upward, can the concern move or be inverted?** Bad: stable policy code is coupled to a volatile framework. Remedy: move the concern outward or define an interface owned by the consuming policy code.
- **Can the affected logic be tested without unrelated components?** Bad: a calculation test requires FastAPI, PostgreSQL, or an external service. Remedy: inject those dependencies and substitute fakes or deterministic test implementations.
- **Does a proposed abstraction establish a meaningful boundary?** Bad: it only adds another wrapper or file. Remedy: remove it or keep the simpler design unless it improves ownership, testability, or extraction.

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

### Self-review questions

- **Does this file contain raw SQL or cursor management?** Bad: SQL is embedded in a router or domain function. Remedy: move it into a repository method expressed in application terms.
- **Does the repository method express an application operation?** Bad: it is a passive wrapper around an unrelated query with no useful boundary. Remedy: give it cohesive ownership or keep the query next to its use case if a repository adds no value.
- **Does the repository contain business calculations or policy decisions?** Bad: financial formulas or domain rules are hidden in persistence code. Remedy: return data from the repository and perform calculations in the domain layer.
- **Is the repository boundary organized around a cohesive capability?** Bad: repositories are split mechanically one per table and an invariant spans several of them. Remedy: group operations around the aggregate or capability that changes together.
- **Can the repository be replaced with a small fake?** Bad: tests must implement a broad database client or connect to PostgreSQL. Remedy: depend on a narrow interface containing only the required operations.

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

### Self-review questions

- **Which records change together and share an invariant?** Bad: the operation is divided by table rather than by the data that must remain consistent. Remedy: identify the aggregate and assign it one application/repository operation.
- **Does one repository operation own the complete aggregate update?** Bad: callers coordinate parent and child writes themselves. Remedy: put the complete aggregate operation behind one repository boundary.
- **Are parent and child replacements in the same transaction?** Bad: one write can commit while the other fails. Remedy: wrap the complete replacement in one database transaction.
- **Could failure leave missing, duplicated, or stale child rows?** Bad: partial output is visible after an error. Remedy: use atomic transactions and test rollback behavior.
- **Did splitting repositories split the transaction boundary?** Bad: related tables are updated independently. Remedy: keep the tables separate if useful, but keep their coordinated update in one transactional operation.

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

### Self-review questions

- **Does this router translate HTTP input into a use-case call and translate the result back into HTTP?** Bad: it owns domain workflows or data-access details. Remedy: keep the route as an HTTP adapter and delegate the use case.
- **Does it contain SQL, cursor management, or substantial business logic?** Bad: transport code performs persistence or calculations. Remedy: move SQL to repositories and policy to application/domain code.
- **Are authentication, error translation, dependency wiring, prefixes, and tags consistent?** Bad: one route bypasses shared checks or maps errors differently without a reason. Remedy: centralize or consistently apply those transport concerns.
- **Would changing transport require changing the use case?** Bad: domain/application code returns HTTP responses or knows route details. Remedy: return ordinary results/errors and translate them only at the transport boundary.

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

### Self-review questions

- **What dependencies does this function need, and are they supplied from outside?** Bad: it constructs clients, repositories, or services internally. Remedy: pass them as arguments or constructor dependencies from the composition root.
- **Does domain code depend on a concrete infrastructure class?** Bad: a calculation imports and requires `DatabaseClient`, a pool, or a driver. Remedy: define a small domain-owned interface such as a `Protocol` and inject the concrete implementation.
- **How many methods would a test fake need to implement?** Bad: the fake must stub a broad client even though the use case calls one method. Remedy: narrow the protocol to the operations this consumer actually uses.
- **Does the function reach into global pool, client, environment, or framework state?** Bad: behavior depends on hidden mutable state. Remedy: supply the needed resource or configuration explicitly.
- **Can it be unit-tested with a fake and no FastAPI or PostgreSQL?** Bad: importing or testing it requires unrelated infrastructure. Remedy: isolate policy code behind injected dependencies and keep framework translation outside it.
- **Where is each dependency created?** Bad: construction is scattered across module-level globals. Remedy: create concrete dependencies in the composition root and pass them down.
- **Is resource lifecycle explicit?** Bad: nobody can tell when a pool opens or closes. Remedy: control startup and shutdown in the application lifespan or worker boundary.

A narrow Python `Protocol` should contain only the methods that the consumer
needs. Infrastructure implementations can satisfy it structurally, while tests
can supply a small fake. Do not introduce an interface merely to add indirection.

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

### Self-review questions

- **Does this module rely on `sys.path`, the current working directory, bare dynamic imports, or filesystem path walks?** Bad: it works only from a particular launch directory or import order. Remedy: use normal package imports and explicit configuration inputs.
- **Are package imports deterministic from different working directories?** Bad: tests and production resolve different modules. Remedy: use the real package path and configure the project/runtime environment deliberately.
- **Does the package expose one deliberate public entry point?** Bad: callers depend on deep internal classes. Remedy: expose a small supported entry point and keep internals private.
- **Would the package retain a clear boundary in a worker process?** Bad: it depends on API routers or hidden process state. Remedy: keep the engine callable through its public entry point with explicit inputs.

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

### Self-review questions

- **Does an `async` function directly call blocking work?** Bad: `subprocess.run`, a synchronous database client, or a long CPU loop blocks the event loop. Remedy: run it through `asyncio.to_thread` or an appropriate executor.
- **Is there a clear worker or executor boundary?** Bad: the router directly owns expensive execution. Remedy: put the adapter in `workers/` and keep the algorithm separate.
- **Does the boundary define timeout, exception, cancellation, and partial-output behavior?** Bad: failures leave behavior or database state undefined. Remedy: specify and test those failure semantics at the execution boundary.
- **Is the execution adapter separate from algorithms and routes?** Bad: worker code contains simulation rules or route definitions. Remedy: make it only bridge orchestration to the simulation package.
- **Could a queue consumer or worker process reuse the runner?** Bad: it requires FastAPI request state. Remedy: accept explicit inputs and keep client/transport concerns outside the runner.

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

### Self-review questions

- **Is there one obvious place where the app, routers, infrastructure, and lifecycle are assembled?** Bad: wiring is scattered across unrelated modules. Remedy: consolidate concrete construction and registration in the composition root.
- **Does importing a module cause construction or other side effects?** Bad: import-time code opens connections, loads configuration unexpectedly, or creates clients. Remedy: construct resources deliberately during application startup or explicit assembly.
- **Are module-level singletons or globals hiding ownership and lifetime?** Bad: callers cannot tell who owns or closes a shared resource. Remedy: pass dependencies explicitly and make lifecycle ownership visible.
- **Can a test replace infrastructure without patching globals?** Bad: tests mutate process-wide state to use a fake. Remedy: construct a smaller app or use dependency overrides at the composition boundary.
- **Is business logic or SQL in the composition root?** Bad: `main.py` becomes another god module. Remedy: keep it limited to configuration, lifecycle, registration, and wiring.

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

### Self-review questions

- **Does every operation accepting user and model identities verify ownership?** Bad: a caller can read or modify a model by guessing its ID. Remedy: enforce ownership in the repository/application boundary for every relevant path.
- **Did moving SQL preserve checks on reads and writes?** Bad: a refactored query no longer joins or filters by the requesting user. Remedy: restore the equivalent authorization predicate and test both authorized and unauthorized cases.
- **Are unauthorized access tests present?** Bad: ownership is trusted but not executable as a regression test. Remedy: add tests proving another user cannot read or modify the model.
- **Are rollback tests present for child-row replacement?** Bad: an insert failure can leave half-written data undetected. Remedy: inject a failure and assert the parent and child records remain consistent.
- **Did the refactor preserve public behavior?** Bad: URLs, response shapes, status codes, or error behavior change unintentionally. Remedy: preserve the contract or document an intentional API change and update its tests.

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

### Self-review questions

- **Is this change modifying PostgreSQL structure, API validation/serialization, or both?** Bad: database and API schema changes are mixed without identifying ownership. Remedy: update each authoritative definition deliberately.
- **If it changes a table, constraint, index, or seed record, is `schema.sql` authoritative?** Bad: the database depends on an undocumented Python model or one-off setup. Remedy: update `schema.sql` and preserve the container initialization path.
- **If it changes an API payload, is the Pydantic model updated independently?** Bad: a Pydantic DTO is treated as PostgreSQL DDL. Remedy: update the DTO for validation/serialization and update SQL separately when the database changes.
- **Does the PostgreSQL container initialize from the intended `schema.sql`?** Bad: local and deployed databases have different structure or seed data. Remedy: verify the mount and initialization process.

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

## Refactor Review Workflow

When reviewing a file or change, first inspect its imports and identify its
layer. Then ask the questions in the corresponding principle section. Finish
with these cross-cutting questions:

- Does the dependency graph still follow transport -> application -> domain -> infrastructure, with infrastructure depending on domain-owned interfaces where needed?
- Can the affected logic be tested without starting unrelated components?
- Did the change preserve ownership checks, transaction boundaries, and public API behavior?
- Would this boundary make a future simulation worker easier to extract?
- Does the change establish a meaningful boundary, or does it only add indirection?
- Would a simpler design satisfy the same principle?
