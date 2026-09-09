# Simplified Gaussian Load Profile Implementation Plan

## Goal

Generate a deterministic annual household load profile from two daily Gaussian
curves. The profile is normalized to sum to `1.0` and overwritten in PostgreSQL
whenever `SimBuilder` creates a simulation.

## Design Decisions

- Use one fixed profile only: `SIMPLE_PROFILE_ID = 1`.
- Always regenerate and overwrite the database row during every simulation
  build.
- Use a fixed random-number-generator seed, making the generated profile
  identical on every build.
- Repeat the same daily curve for all 365 days.
- Add small, zero-mean random noise independently to every hourly value. Noise
  may be negative, but final values must not be negative.
- Use hourly resolution: 365 days x 24 hours = 8,760 values.
- Ignore the configured `baseload_profile_id`; simulations always use the
  simple profile.

## Existing Constraints

- The `loadprofiles` table has a unique `profile_id` and stores the profile in
  a `DOUBLE PRECISION[]` column (`backend/schema.sql`).
- `BaseLoad` requires the loaded profile array to sum to `1.0`, within a
  tolerance of `1e-6` (`backend/src/domains/ferntree/components/dev/baseload.py`).
- `SimBuilder` obtains profiles through its synchronous `PostgresClient`
  (`backend/src/domains/ferntree/sim_builder.py`).

## Implementation Steps

### 1. Add a Gaussian profile generator

Create `backend/src/domains/loadprofiles/gaussian_profile.py` with no import-time
side effects.

Define constants:

- `SIMPLE_PROFILE_ID = 1`
- `SIMPLE_PROFILE_TYPE = "simplified gaussian loadprofile"`
- Morning peak: center `7h`, standard deviation `2h`, relative scale `0.8`.
- Evening peak: center `19h`, standard deviation `2.5h`, relative scale `1.0`.
- A small noise standard deviation and a fixed RNG seed.

Implement:

- A Gaussian helper evaluating `scale * exp(-(hour - center)^2 / (2 * sigma^2))`
  for the 24 hourly values.
- `generate_daily_profile()`, returning the element-wise sum of the morning and
  evening Gaussian curves.
- `generate_annual_profile()`, which:
  1. Repeats the daily curve 365 times.
  2. Adds seeded, small, normally distributed noise to each hourly value.
  3. Clamps values to zero or greater, preventing negative power values.
  4. Treats the resulting values as kW and normalizes the annual array by its
     sum so that it sums to `1.0`.
  5. Returns the profile as `list[float]` for Psycopg/PostgreSQL.

Normalization is the essential final invariant. The initial physical scale does
not affect the final normalized array, but the code should make the kW intent
clear and document this relationship.

### 2. Add a load-profile upsert to the synchronous DB client

Add an `ensure_load_profile()` method to
`backend/src/db/sync_client/client.py`.

The method accepts the profile ID, profile type, and generated array, then uses
an upsert and commits the transaction:

```sql
INSERT INTO loadprofiles (profile_id, type, load_profile)
VALUES (%s, %s, %s)
ON CONFLICT (profile_id) DO UPDATE SET
    type = EXCLUDED.type,
    load_profile = EXCLUDED.load_profile
```

This avoids duplicates while intentionally refreshing the fixed profile on every
simulation build. The fixed seed means each refresh writes the same content.

### 3. Seed from SimBuilder and always consume the simple profile

Update `backend/src/domains/ferntree/sim_builder.py`.

After creating `self.db_client` in `SimBuilder.__init__`:

1. Generate the annual Gaussian profile.
2. Call `self.db_client.ensure_load_profile()` with the fixed profile constants.

When constructing `BaseLoad` in `build_simulation()`, fetch
`SIMPLE_PROFILE_ID` directly rather than using
`sim_config["baseload_profile_id"]`.

The persisted `baseload_profile_id` column and configuration are left unchanged
for now, but no longer affect runtime behavior.

## Verification

Add `backend/tests/test_gaussian_profile.py` with tests that verify:

- The annual profile contains exactly 8,760 values.
- All values are non-negative after noise handling.
- The array sums to `1.0` within `1e-6`.
- Two calls produce equal values because the RNG seed is fixed.
- The evening peak is higher than the morning peak, reflecting scales `1.0` and
  `0.8`.

Also verify the integration path:

- Build a simulation and confirm the simple profile is written and loaded.
- Confirm `BaseLoad` does not raise its normalization error.
- Build again and confirm the row is updated rather than duplicated.
- Run the project's `ruff`, `ty`, and relevant pytest commands.

## Files to Change

| File | Change |
| --- | --- |
| `backend/src/domains/loadprofiles/gaussian_profile.py` | New deterministic two-Gaussian annual-profile generator. |
| `backend/src/db/sync_client/client.py` | Add `ensure_load_profile()` PostgreSQL upsert. |
| `backend/src/domains/ferntree/sim_builder.py` | Generate and write the fixed profile; always use its ID. |
| `backend/tests/test_gaussian_profile.py` | Add generator unit tests. |

## Cleanup Completed

- Removed the obsolete ALPG, CKW, and bronze/silver/gold load-profile scripts.
- Removed the unused `baseload_profile_id` field from schemas, configuration,
  persistence, and the database schema.
- The existing `loadprofiles` table continues to support the simple profile
  without schema changes.
