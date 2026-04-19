# UI Redesign Report

## Scope

This report documents the completed implementation work for **Phase 1: Foundation Tokens and Global Reset** from `docs/ui/redesign_implementation_plan.md`.

## Decisions Applied

- Focus color for global keyboard accessibility states: `--copper-raw`.
- Accent role for secondary positive/semantic accents: `--copper-oxidized`.

## Files Changed

- `frontend/src/styles/global.css`

## Implemented Changes

### 1) Token Foundation Replacement

Updated `:root` to include the Tinkerer's Grid semantic token set:

- `--bg-base`, `--bg-surface`, `--bg-hover`
- `--border-metal`
- `--text-primary`, `--text-secondary`
- `--copper-raw`, `--copper-hover`, `--copper-oxidized`
- `--danger-red`

Also set geometry/elevation baseline tokens:

- `--radius: 0`
- `--shadow: none`
- `--shadow-md: none`

To reduce regression risk in Phase 1, legacy token names were kept as compatibility aliases and mapped to the new semantic palette.

### 2) Global Typography Baseline

Applied global typography defaults in `html, body`:

- Single sans-serif family (`'IBM Plex Sans', 'Segoe UI', Helvetica, Arial, sans-serif`)
- `font-variant-numeric: tabular-nums`
- Base text/background mapped to `--text-primary` / `--bg-base`

### 3) Global Geometry and Elevation Reset

Applied base visual reset on universal selector:

- `border-radius: 0`
- `box-shadow: none`

This enforces the bare-metal requirement and removes rounded/shadowed styling globally.

### 4) Base Surface and Shell Updates

Updated core app shell surfaces:

- `#app` now uses `--bg-base` / `--text-primary`
- `#topnav` and `#sidenav` background switched from `white` to `--bg-surface`
- Shared white panel surfaces moved to dark surfaces in key primitives:
  - `.card`
  - `.loading-card`
  - `dialog`
  - `.blog-card`
  - `.blog-post-article`
  - `.landing-cta-strip`
  - `.landing-cta-primary`

### 5) Interactive Defaults and Focus Accessibility

Updated global interactive defaults:

- `a` now defaults to copper with hover using `--copper-hover`
- `button` defaults to dark surface + metal border
- `input/select/textarea` defaults to dark surface + metal border
- Global `:focus-visible` added with `2px solid var(--copper-raw)` and `outline-offset: 2px`

Updated existing control-specific focus states to copper:

- `.sidebar-select:focus`
- `.date-label input[type="date"]:focus`

Removed `outline: none` from `.form-input` to avoid suppressing keyboard focus visuals.

### 6) Literal Color Cleanup (Phase 1 baseline)

Converted selected hardcoded light-mode literals in shared/foundation areas:

- `.fin-warning` background/border to tokenized dark + danger treatment
- `.landing-hero` gradient replaced with flat `--bg-surface`

## Verification

Build verification completed:

- Command: `npm run build` (in `frontend/`)
- Result: success

## Notes and Deferred Work

The following are intentionally deferred to later phases per plan:

- Full component variant redesign (buttons/forms/cards behavior details)
- Navigation active-state redesign and shell behavior refinements
- Page-level visual harmonization across all sections
- Chart palette centralization and tokenized chart theme module

Phase 1 establishes the high-risk global foundation without restructuring page markup.
